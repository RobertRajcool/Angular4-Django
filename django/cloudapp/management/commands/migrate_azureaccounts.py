import requests
import datetime
import os
import json
from redington import settings
from django.core.management import BaseCommand
import csv
from customers.models import Customers, CustomerContacts, CloudAccounts
from partner.models import Partner, PartnerUserDetails
from products.models import Products, VendorDetails
from django.utils.dateparse import parse_datetime
from orders.models import Orders,OrderItems,Subscriptions
import codecs
from cloudapp.generics.functions import generate_order_number

from background_scripts.microsoft.microsoft_base import MicrosoftBase


class Command(BaseCommand):
    help = "This command migrates Azure Accounts"

    def handle(self, *args, **options):
        migration_csvs = os.path.join(settings.BASE_DIR, 'migrations')

        existing_azure_accounts = os.path.join(migration_csvs, 'existing_azure_accounts.csv')
        customers = json.load(open('/tmp/customer_map.json', 'r'))

        m = MicrosoftBase()
        headers = m.getAccessHeaders()

        with open(existing_azure_accounts, 'r', encoding='latin1') as csvfile:
            for row in list(csv.reader(csvfile)):
                print("Processing: %s" %(row[5]))
                customer_id = row[13]
                reference_number = None
                if not customer_id:
                    # insert into customers, cloudaccounts
                    customer = Customers()
                    partner = Partner.objects.filter(jba_code=row[11].strip())
                    if not partner:
                        print("Cannot find partner: %s" %(row[11]))
                        continue
                    else:
                        partner = partner[0]

                    customer.partner = partner
                    customer.company_name = row[5]
                    customer.address = row[5]
                    customer.save()

                    customer_contact1 = CustomerContacts()
                    customer_contact1.customer = customer
                    customer_contact1.name = ''
                    customer_contact1.save()

                    customer_contact2 = CustomerContacts()
                    customer_contact2.customer = customer
                    customer_contact2.name = ''
                    customer_contact2.save()
                    customer_id = customer.id
                elif not customer_id in customers:
                    print("Cannot find customers: %s" %(customer_id))
                    continue
                else:
                    customer = Customers.objects.get(pk=customers[customer_id])

                partner = PartnerUserDetails.objects.filter(partner=customer.partner)
                orders = Orders()
                if not row[14]:
                    orders.order_number = generate_order_number()
                else:
                    orders.order_number = row[14]
                orders.status = 6
                orders.customer = customer
                orders.partner = customer.partner
                orders.vendor = VendorDetails.objects.get(pk=3)
                orders.total_cost = 0
                orders.created_by = partner[0].user
                orders.created_at = datetime.datetime.now()
                orders.modified_by = partner[0].user
                orders.billing_type = 'annually'
                orders.billing_completed = 0
                orders.save()
                reference_number = orders.id

                order_items = OrderItems()
                order_items.order = orders
                order_items.product = Products.objects.get(product_sku_code='MS-AZR-0145P')
                order_items.quantity = 1
                order_items.discount = 0
                order_items.price_per_unit = 0
                order_items.cost = 0
                order_items.created_by = partner[0].user
                order_items.created_at = datetime.datetime.now()
                order_items.modified_by = partner[0].user
                order_items.save()

                cloud_account = CloudAccounts.objects.filter(customer=customer,
                                                             type='MS',
                                                             vendor=VendorDetails.objects.get(pk=3))
                if not cloud_account.exists():
                    cloud_account = CloudAccounts()
                    cloud_account.customer = customer
                    cloud_account.vendor = VendorDetails.objects.get(pk=3)
                    cloud_account.type = 'MS'
                    cloud_account.active = True
                    partner = PartnerUserDetails.objects.filter(partner=customer.partner)
                    cloud_account.created_by = partner[0].user
                    cloud_account.created_at = datetime.datetime.now()
                    cloud_account.modified_by = partner[0].user
                    discount = 10

                    reference_number = orders.order_number
                    if row[8]:
                        discount = row[8]
                    cloud_account.details = {
                        'active': True,
                        'tenant_id': row[16],
                        'domain_name': row[17],
                        'discount_status': 'Approved',
                        'standard_discount': discount,
                        'allow_order': 'Yes',
                        'reference_number': reference_number
                    }
                    cloud_account.save()

                # Insert into Subscriptions
                url = str.format(
                        'https://api.partnercenter.microsoft.com/v1/customers/{}/subscriptions/{}',
                        row[16], row[15])

                subscriptions_out = requests.get(url, headers=headers)

                if subscriptions_out.status_code == 401:
                    # Reprocess
                    m = MicrosoftBase()
                    headers = m.getAccessHeaders()
                    subscriptions_out = requests.get(url, headers=headers)

                if subscriptions_out.status_code == 200:
                    subscriptions = json.loads(codecs.decode(subscriptions_out.content, 'utf-8-sig'))

                    # Insert into Subscription
                    subscription = Subscriptions()
                    subscription.customer = customer
                    subscription.order = orders
                    subscription.product = Products.objects.get(product_sku_code='MS-AZR-0145P')
                    subscription.subscription = subscriptions['id']
                    subscription.creation_date = parse_datetime(subscriptions['creationDate'])
                    subscription.ms_order_id = subscriptions['orderId']
                    subscription.name = subscriptions['offerName']
                    subscription.quantity = subscriptions['quantity']
                    subscription.unit_type = subscriptions['unitType']
                    subscription.effective_start_date = parse_datetime(subscriptions['effectiveStartDate'])
                    subscription.commitment_end_date = parse_datetime(subscriptions['commitmentEndDate'])
                    subscription.auto_renew_enabled = subscriptions['autoRenewEnabled']
                    subscription.status = subscriptions['status']
                    subscription.is_trial = subscriptions['isTrial']
                    subscription.billing_type = subscriptions['billingType']
                    subscription.billing_cycle = subscriptions['billingCycle']
                    subscription.contract_type = subscriptions['contractType']
                    subscription.save()


