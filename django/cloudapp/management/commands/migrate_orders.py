import csv
import os
import json
import datetime
import pprint
from django.core.management import BaseCommand
from django.utils.dateparse import parse_datetime

from redington import settings
from customers.models import Customers, CloudAccounts
from products.models import VendorDetails, Products
from orders.models import Orders,OrderItems, Subscriptions
from partner.models import PartnerUserDetails

import requests
import codecs

from background_scripts.microsoft.microsoft_base import MicrosoftBase

# RAJA: TODO: Remember to change users_reduser firstname/lastname to varchar(100) as some names are long
class Command(BaseCommand):
    help = "This command migrates Orders from old Redington cloud to new system"

    def handle(self, *args, **options):

        microsoft_customers = '/tmp/customers.json'

        migration_csvs = os.path.join(settings.BASE_DIR, 'migrations')
        order_csv = os.path.join(migration_csvs, 'orders.csv')

        microsoft_customers = '/tmp/customers.json'
        existing_microsoft_domains = os.path.join(migration_csvs, 'microsoft_domains.csv')

        m = MicrosoftBase()
        headers = m.getAccessHeaders()
        """headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6InowMzl6ZHNGdWl6cEJmQlZLMVRuMjVRSFlPMCIsImtpZCI6InowMzl6ZHNGdWl6cEJmQlZLMVRuMjVRSFlPMCJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLndpbmRvd3MubmV0IiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvN2MyNjFhMTktM2VmZS00ZTZjLTg5ZGEtZDBlNmVhOTc0MzZkLyIsImlhdCI6MTQ5NTA2Nzc5NSwibmJmIjoxNDk1MDY3Nzk1LCJleHAiOjE0OTUwNzE2OTUsImFpbyI6IlkyWmdZT0N1MVh0NVdlS2Q0Y2RKTHNhRyszNGxBQUE9IiwiYXBwaWQiOiI5MzFhYTEzNy1mOGQ4LTQ3ZWMtYjZmNS04Y2ZlNzQ5ZWEyOGEiLCJhcHBpZGFjciI6IjEiLCJpZHAiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83YzI2MWExOS0zZWZlLTRlNmMtODlkYS1kMGU2ZWE5NzQzNmQvIiwib2lkIjoiODk5YTg4NTUtMWU0Mi00OTVkLThlOTEtOGI0ODFkYTc3M2JkIiwicm9sZXMiOlsiRGlyZWN0b3J5LlJlYWQuQWxsIiwiRGlyZWN0b3J5LlJlYWRXcml0ZS5BbGwiLCJEb21haW4uUmVhZFdyaXRlLkFsbCJdLCJzdWIiOiI4OTlhODg1NS0xZTQyLTQ5NWQtOGU5MS04YjQ4MWRhNzczYmQiLCJ0aWQiOiI3YzI2MWExOS0zZWZlLTRlNmMtODlkYS1kMGU2ZWE5NzQzNmQiLCJ1dGkiOiJLTFZHMThwNHBreTFnaGxCS1I4Q0FBIiwidmVyIjoiMS4wIn0.oW6di_XNbT_ZQWNXWvVp0UaavkGg_JEQany5jog5ETeM_xWaRhAdv2L20FIIQ0H82N4yiHKZGG0N_VuYxU6_-jB4uckv6Y3n2KJnt2tpNtdJlZgbf3mSgLyP4gkOTkMFdRBW_swYAvnU03ZyTCN-eQxoV3n5S0eQkkrm8nCIEA1wcpwo7IWwTswKxIyIq44yM1PxjeIvHBp6P7IBP4Y8rDBaz0dZOWN_J4lpDi2Kr9v0VsGeHbgfkV8Ra3pj8q3uSoGZfe5iZ5yI_mki8JELMFsoMkO02v8-WfUiy_Fq6vkJwGI-0DmgWkX0nwvMsTPjSmInWbYApxvbFnX8_hJvpw',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }"""

        customers = json.load(open('/tmp/customer_map.json', 'r'))

        processed_orders = json.load(open('/tmp/orders.json', 'r'))

        with open(order_csv, 'r', encoding='latin1') as csvfile:
            for row in reversed(list(csv.reader(csvfile))):
                order_status = row[6]
                if order_status == 'Provision':
                    customer = None
                    try:
                        customer = Customers.objects.get(pk=customers[row[1]])
                    except:
                        print("Could not find Customer for %s" %(row[1],))
                        continue

                    # Handle only msft for now
                    vendor = row[11]
                    if vendor == 'MICROSOFT' or vendor == 'Office':
                        if not row[17]:
                            print("Could not find order for order: %s " %(row[2],))
                            continue

                        if row[17] == 'Microsoft Azure':
                            print("Azure Order: %s" %(row[2],))
                            pass        # Skip for now
                        else:
                            if row[2] in processed_orders:
                                continue    # Skip as its already processed

                            print("Processing Order: %s" %(row[2],))
                            cloud_account_object = CloudAccounts.objects.filter(customer=customer,
                                                                      type='MS',
                                                                      vendor=VendorDetails.objects.get(pk=4))
                            if not cloud_account_object:
                                print("Could not find Cloud Account for order: %s" %(row[2],))
                                continue

                            cloud_account = cloud_account_object.first()
                            if 'tenant_id' not in cloud_account.details:
                                print("Could not find domain name for Order: %s, Check with Redington" %(row[2],))
                                continue

                            tenant_id = cloud_account.details['tenant_id']

                            url = str.format('https://api.partnercenter.microsoft.com/v1/customers/{}/subscriptions',
                                             tenant_id)

                            subscriptions_out = requests.get(url, headers=headers)

                            if subscriptions_out.status_code == 401:
                                # Reprocess
                                m = MicrosoftBase()
                                headers = m.getAccessHeaders()
                                subscriptions_out = requests.get(url, headers=headers)

                            if subscriptions_out.status_code == 200:
                                subscriptions = json.loads(codecs.decode(subscriptions_out.content, 'utf-8-sig'))
                                items = subscriptions['items']
                                subscription_available = False
                                for item in items:
                                    if item['offerName'] == row[17]:
                                        # Insert into Orders, ordersItems and subscriptions
                                        subscription_available = True

                                        # Check if Order placed, then insert into items
                                        existing_order = Orders.objects.filter(order_number = row[2])
                                        if existing_order:
                                            # Get Order Reference
                                            order_pk = existing_order[0].pk
                                        else:
                                            # Insert into Order
                                            order = Orders()
                                            order.order_number = row[2]
                                            order.pk = int(row[2][3:])
                                            order.status = 6
                                            order.partner = customer.partner
                                            order.customer = customer
                                            order.vendor = VendorDetails.objects.get(pk=4)
                                            order.total_cost = 0
                                            try:
                                                dateVal = datetime.datetime.strptime(row[4], '%d/%m/%y')
                                            except:
                                                dateVal = datetime.datetime.strptime(row[4], '%d/%m/%Y')
                                            order.created_at = dateVal
                                            order.created_by = PartnerUserDetails.objects.filter(partner = customer.partner)[0].user
                                            order.billing_type = item['billingCycle']
                                            if order.billing_type == 'monthly':
                                                order.billing_completed = 0
                                            else:
                                                order.billing_completed = 1
                                            order.modified_by_id = PartnerUserDetails.objects.filter(partner = customer.partner)[0].user.pk

                                            order.save()
                                            order_pk = order.pk

                                        # Insert into Order Items
                                        orderItem = OrderItems()
                                        orderItem.order = Orders.objects.get(pk=order_pk)
                                        orderItem.product = Products.objects.get(pk=4)
                                        orderItem.quantity = item['quantity']
                                        orderItem.discount = 0      # Check with Redington
                                        orderItem.price_per_unit = row[15]
                                        orderItem.cost = float(item['quantity']) * float(row[15])
                                        try:
                                            dateVal = datetime.datetime.strptime(row[4], '%d/%m/%y')
                                        except:
                                            dateVal = datetime.datetime.strptime(row[4], '%d/%m/%Y')
                                        orderItem.created_at = dateVal
                                        orderItem.created_by = PartnerUserDetails.objects.filter(partner=customer.partner)[
                                            0].user
                                        orderItem.modified_by_id = PartnerUserDetails.objects.filter(partner=customer.partner)[
                                            0].user.pk
                                        orderItem.save()

                                        # Insert into Subscription
                                        subscription = Subscriptions()
                                        subscription.customer = customer
                                        subscription.order = Orders.objects.get(pk=order_pk)
                                        subscription.product = Products.objects.get(pk=4)
                                        subscription.subscription = item['id']
                                        subscription.creation_date = parse_datetime(item['creationDate'])
                                        subscription.ms_order_id = item['orderId']
                                        subscription.name = item['offerName']
                                        subscription.quantity = item['quantity']
                                        subscription.unit_type = item['unitType']
                                        subscription.effective_start_date = parse_datetime(item['effectiveStartDate'])
                                        subscription.commitment_end_date = parse_datetime(item['commitmentEndDate'])
                                        subscription.auto_renew_enabled = item['autoRenewEnabled']
                                        subscription.status = item['status']
                                        subscription.is_trial = item['isTrial']
                                        subscription.billing_type = item['billingType']
                                        subscription.billing_cycle = item['billingCycle']
                                        subscription.contract_type = item['contractType']
                                        subscription.save()

                                        processed_orders[row[2]] = order_pk
                                        json.dump(processed_orders, open('/tmp/orders.json', 'w'))    # Write back for further process

                                if not subscription_available:
                                    pprint.pprint("Couldnt find subscription: %s for: %s and order: %s" % (
                                        row[17], tenant_id, row[2]))
                                    continue
                            else:
                                pprint.pprint("No subscriptions found for %s for order %s" % (
                                    tenant_id, row[2]))
                                continue
                    else:
                        # Handle other vendors  (Amazon)
                        pass
