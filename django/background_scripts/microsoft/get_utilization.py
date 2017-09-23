from decimal import Decimal

from . import microsoft_base
from redington import settings
from cloudtemplates.models import CloudRates
from billing.models import CloudServiceConsumptions
from customers.models import Customers, CloudAccounts
from products.models import Products, VendorDetails
from django.db.models import ObjectDoesNotExist, Q
from django.core.exceptions import MultipleObjectsReturned
from cloudapp.defaults import AppDefaults
import datetime
from datetime import timedelta, tzinfo
from django.utils import timezone
from cloudapp.generics.caculator import calculate_azure_partner_cost

import pprint
import requests
import subprocess
import os.path
import json
import functools
import uuid
import sys
import pytz


class UtilizationRecords(microsoft_base.MicrosoftBase):
    def __init__(self, tenantId, subscriptionId, startDate, endDate):
        super(UtilizationRecords, self).__init__()
        self.tenantId = tenantId
        self.subscriptionId = subscriptionId
        self.startDate = startDate
        self.endDate = endDate

        self.consolidated_rates = {}
        self.grouped_records = {}
        self.grouped_calculations = {}

        self.ignored_rate_names = [
            'Data Transfer In (GB)',
        ]

        self.consolidated_rate_names = [
            'Data Transfer Out (GB)'
        ]

    # Main method to get the utilizations
    def getUtilization(self):
        access_headers = self.getAccessHeaders()

        url = 'https://api.partnercenter.microsoft.com/v1/customers/' \
              '{}/subscriptions/{}/utilizations/azure?' \
              'start_time={}&end_time={}&granularity=Daily&show_details=True'. \
            format(self.tenantId, self.subscriptionId, self.startDate, self.endDate)
        utilization_records_out = requests.get(url, headers=access_headers)
        utilization_records_out.encoding = 'utf-8-sig'
        utilization_records = utilization_records_out.text

        self.process_records(utilization_records, self.grouped_records, self.grouped_calculations,
                             self.consolidated_rates)

        if len(self.consolidated_rates) > 0:
            """ Querying vendor & customer """
            vendor = VendorDetails.objects.filter(vendor_name=AppDefaults.cloud_vendor_codes(return_as='name',
                                                                                             query_str='MS')).first()
            account_type = AppDefaults.cloud_vendor_codes(return_as='code', query_str=vendor.vendor_name)

            cloud_accounts = CloudAccounts.objects.filter(details__tenant_id=self.tenantId.upper(),
                                                          type=account_type
                                                          )
            """ Try for lowercase """
            if not cloud_accounts.exists():
                cloud_accounts = CloudAccounts.objects.filter(details__tenant_id=self.tenantId.lower(),
                                                              type=account_type
                                                              )

            customer = None
            if cloud_accounts.exists():
                cloud_account = cloud_accounts.first()
                customer = cloud_account.customer

                customer_cloud_acc_details = cloud_account.details
                standard_discount = 10
                if 'standard_discount' in customer_cloud_acc_details \
                        and customer_cloud_acc_details['standard_discount'] is not None \
                        and customer_cloud_acc_details['standard_discount'] != '':
                    standard_discount = float(customer_cloud_acc_details['standard_discount'])

            for name, entries in self.consolidated_rates.items():
                by_region = {}
                totals = 0
                for entry in entries:
                    name_with_location = str.format('{}|{}', name, entry[6])
                    region_entry = by_region.setdefault(name_with_location, [])
                    region_entry.append(entry)
                    totals = totals + entry[7]

                for item in by_region:
                    split_values = item.split('|')
                    if split_values:
                        product_name = split_values[0]
                        location = split_values[1]

                        daily_records = by_region[item]
                        for rec in daily_records:
                            start_date = self.str_to_datetime(rec[0])
                            date_of_recording = None
                            if start_date.month == 1:
                                if start_date.day >= 22:
                                    date_of_recording = datetime.datetime(start_date.year, start_date.month, 22, 0, 0,
                                                                          0, tzinfo=pytz.UTC)
                                else:
                                    date_of_recording = datetime.datetime(start_date.year - 1, 12, 22, 0, 0, 0,
                                                                          tzinfo=pytz.UTC)
                            else:
                                if start_date.day >= 22:
                                    date_of_recording = datetime.datetime(start_date.year, start_date.month, 22, 0, 0,
                                                                          0, tzinfo=pytz.UTC)
                                else:
                                    date_of_recording = datetime.datetime(start_date.year, start_date.month - 1, 22, 0,
                                                                          0, 0, tzinfo=pytz.UTC)

                            # Check if there isa  record on the 22nd (as we store all storage only on the 22nd
                            consumption = CloudServiceConsumptions.objects.filter(
                                linked_account_id=self.tenantId,
                                subscription_id=self.subscriptionId,
                                item_description=product_name,
                                region=location,
                                usage_start_date=date_of_recording
                            )

                            cloud_rate = CloudRates.objects.get(uuid=rec[2])
                            if consumption.exists():
                                consumption = consumption[0]
                                consumption.usage_quantity = consumption.usage_quantity + Decimal(rec[7])
                                if consumption.usage_quantity > 5:
                                    cost = calculate_azure_partner_cost(
                                        (float(consumption.usage_quantity) - 5) * float(cloud_rate.rate),
                                        standard_discount)
                                    consumption.unblended_cost = Decimal(cost)

                                consumption.save()
                            else:
                                consumption = CloudServiceConsumptions()
                                consumption.customer = customer
                                consumption.vendor = vendor
                                consumption.record_id = cloud_rate.uuid
                                consumption.usage_start_date = date_of_recording

                                end_date = date_of_recording + timedelta(days=1)
                                consumption.usage_end_date = end_date
                                consumption.payer_account_id = self.csp_domain
                                consumption.linked_account_id = self.tenantId
                                consumption.pricing_plan_id = ''
                                consumption.product_name = rec[4]
                                consumption.usage_type = rec[5]
                                consumption.item_description = rec[3]
                                consumption.usage_quantity = rec[7]
                                consumption.region = location if location else 'N/A'
                                consumption.rate_id = cloud_rate.id
                                consumption.subscription_id = self.subscriptionId
                                consumption.unblended_cost = 0  # Always 0 when we start
                                consumption.save()

                                # pprint.pprint(by_region)

        pprint.pprint(self.grouped_records)
        pprint.pprint(self.grouped_calculations)

        total = functools.reduce(lambda x, y: x + y, self.grouped_calculations.values())
        pprint.pprint(total)

    def str_to_datetime(self, dt_string):
        """ Converts date string into UTC datetime object """
        return datetime.datetime.strptime(dt_string, "%Y-%m-%d").replace(
            tzinfo=timezone.utc) if dt_string is not None else datetime.datetime.utcnow()

    # Recursive Block to keep returning records till we dont have any more continuation records...SPIN SPIN SPIN
    def process_records(self, utilization_records, grouped_records, grouped_calculations, consolidated_rates):
        out_file = open('/tmp/{}.json'.format(self.subscriptionId), 'w')
        out_file.write(utilization_records)
        out_file.close()

        if os.path.exists('/tmp/{}.json'.format(self.subscriptionId)):
            proc = subprocess.Popen(
                ["jq",
                 "-c",
                 '.items[] | [(.usageStartTime | sub("(?<before>.*)[-+]\\\\d{2}:\\\\d{2}"; .before ) | '
                 'strptime("%Y-%m-%dT%H:%M:%S") | strftime("%Y-%m-%d")),  '
                 '(.usageEndTime | sub("(?<before>.*)[-+]\\\\d{2}:\\\\d{2}"; .before ) | '
                 'strptime("%Y-%m-%dT%H:%M:%S") | strftime("%Y-%m-%d")), '
                 '.resource.id, .resource.name, .resource.category, .resource.subcategory, .resource.region, .quantity]'
                 ],
                stdout=subprocess.PIPE,
                stdin=open('/tmp/{}.json'.format(self.subscriptionId)))

            """ Querying vendor & customer """
            vendor = VendorDetails.objects.filter(vendor_name=AppDefaults.cloud_vendor_codes(return_as='name',
                                                                                             query_str='MS')).first()

            account_type = AppDefaults.cloud_vendor_codes(return_as='code', query_str=vendor.vendor_name)

            cloud_accounts = CloudAccounts.objects.filter(details__tenant_id=self.tenantId.upper(),
                                                          type=account_type
                                                          )
            """ Try for lowercase """
            if not cloud_accounts.exists():
                cloud_accounts = CloudAccounts.objects.filter(details__tenant_id=self.tenantId.lower(),
                                                              type=account_type
                                                              )
            customer = None
            if cloud_accounts.exists():
                cloud_account = cloud_accounts.first()
                customer = cloud_account.customer

                customer_cloud_acc_details = cloud_account.details
                standard_discount = 10
                if 'standard_discount' in customer_cloud_acc_details \
                        and customer_cloud_acc_details['standard_discount'] is not None \
                        and customer_cloud_acc_details['standard_discount'] != '':
                    standard_discount = float(customer_cloud_acc_details['standard_discount'])
            else:
                sys.exit(
                    '\033[0;37;41mSeems there is no customer for tenant id: %s. Terminating ...\033[0m' % self.tenantId)

            for line in proc.stdout.readlines():
                line = json.loads(line.decode())

                utilization_start_date = self.str_to_datetime(line[0])
                utilization_end_date = self.str_to_datetime(line[1])
                resource_uuid = line[2]
                name = line[3]
                category = line[4]
                subcategory = line[5]
                location = line[6]
                quantity = line[7]

                if name in self.ignored_rate_names:
                    continue

                if name in self.consolidated_rate_names:
                    consolidated_rate_name_value = consolidated_rates.setdefault(name, [])
                    consolidated_rate_name_value.append(line)
                    continue

                try:
                    cloud_rate = CloudRates.objects.get(uuid=resource_uuid)
                    full_name = str.format('{}|{}|{}|{}', category, subcategory, name, location)
                    current_util = grouped_records.setdefault(full_name, 0)
                    grouped_records[full_name] = current_util + quantity

                    current_prices = grouped_calculations.setdefault(full_name, 0)
                    grouped_calculations[full_name] = current_prices + (quantity * float(cloud_rate.rate))

                    # Store in the DB
                    consumption = CloudServiceConsumptions()
                    consumption.customer = customer
                    consumption.vendor = vendor
                    consumption.record_id = cloud_rate.uuid
                    consumption.usage_start_date = utilization_start_date
                    consumption.usage_end_date = utilization_end_date
                    consumption.payer_account_id = self.csp_domain
                    consumption.linked_account_id = self.tenantId
                    consumption.pricing_plan_id = ''
                    consumption.product_name = category
                    consumption.usage_type = subcategory
                    consumption.item_description = name
                    consumption.usage_quantity = quantity
                    consumption.region = location if location else 'N/A'
                    consumption.rate_id = cloud_rate.id
                    consumption.subscription_id = self.subscriptionId
                    consumption.unblended_cost = calculate_azure_partner_cost(quantity * float(cloud_rate.rate),
                                                                              standard_discount)
                    consumption.save()

                except ObjectDoesNotExist:
                    print(
                        "could not find for %s %s %s %s %s" % (
                            category, subcategory, name, location, utilization_start_date))

            # Delete the file
            os.remove('/tmp/{}.json'.format(self.subscriptionId))

        # Check if there are further entries
        json_output = json.loads(utilization_records)
        if 'next' in json_output['links']:
            url = 'https://api.partnercenter.microsoft.com/v1/' + json_output['links']['next']['uri']
            continuation_header = {json_output['links']['next']['headers'][0]['key']:
                                       json_output['links']['next']['headers'][0]['value']}
            access_headers = self.getAccessHeaders()
            access_headers.update(continuation_header)

            utilization_records_out = requests.get(url, headers=access_headers)
            utilization_records_out.encoding = 'utf-8-sig'
            utilization_records = utilization_records_out.text
            self.process_records(utilization_records, grouped_records, grouped_calculations, consolidated_rates)
