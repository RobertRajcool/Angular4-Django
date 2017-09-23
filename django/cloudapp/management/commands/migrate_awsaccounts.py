import requests
import datetime
import os
import json
from redington import settings
from django.core.management import BaseCommand
import csv
from customers.models import Customers, CloudAccounts, PendingRequests
from partner.models import PartnerUserDetails
from products.models import VendorDetails

from background_scripts.microsoft.microsoft_base import MicrosoftBase


class Command(BaseCommand):
    help = "This command migrates AWS Accounts"

    def handle(self, *args, **options):
        migration_csvs = os.path.join(settings.BASE_DIR, 'migrations')

        existing_aws_accounts = os.path.join(migration_csvs, 'aws_accounts.csv')
        existing_orders = os.path.join(migration_csvs, 'orders.csv')

        customers = json.load(open('/tmp/customer_map.json', 'r'))

        aws_with_payer = os.path.join(migration_csvs, 'aws_with_payer.csv')
        aws_orders = {}
        with open(existing_orders, 'r', encoding='latin1') as csvfile:
            for row in list(csv.reader(csvfile)):
                if row[11] == 'AMAZON':
                    aws_orders[row[2]] = {
                        'customerId': row[1],
                        'partnerId': row[3],
                        'createdDate': row[4],
                        'status': row[6]
                    }

        # This is from the aws_accounts obtained from old portal to get iam details
        order_based_aws_details = {}
        with open(existing_aws_accounts, 'r', encoding='latin1') as csvfile:
            for row in list(csv.reader(csvfile)):
                if not row[2]:
                    continue

                order_based_aws_details[row[2]] = {
                    'root_email': row[4],
                    'iam_username': row[5],
                    'iam_url': row[6]
                }

        with open(aws_with_payer, 'r', encoding='latin1') as csvfile:
            for row in list(csv.reader(csvfile)):
                order_rec_available = True
                if not row[0] in aws_orders:
                    order_rec_available = False
                    print("In Payer account, not in orders database : %s" %(row[0]))
                    continue  # TODO: Need to check with Redington

                if order_rec_available:
                    aws_order_rec = aws_orders[row[0]]
                    customer = None
                    try:
                        customer = Customers.objects.get(pk=customers[aws_order_rec['customerId']])
                    except KeyError:
                        print("Coudlnt find Customer for %s" % (aws_order_rec['customerId'],))
                        continue

                    cloud_account_exists = CloudAccounts.objects.filter(
                        customer=customer,
                        vendor=VendorDetails.objects.get(pk=1),
                        type='AWS'
                    )
                    if cloud_account_exists.exists():
                        continue  # Already processed

                    if not row[3] in order_based_aws_details:
                        root_email = ''
                        iam_username = ''
                        iam_url = ''
                    else:
                        root_email = order_based_aws_details[row[3]]['root_email']
                        iam_username = order_based_aws_details[row[3]]['iam_username']
                        iam_url = order_based_aws_details[row[3]]['iam_url']

                    aws_details = dict()
                    aws_details.update({'payer_account_id': '',
                                        'account_id': '',
                                        'iam_username': '',
                                        'iam_password': '',
                                        'iam_url': '',
                                        'root_email': '',
                                        'friendly_name': '',
                                        'delivery_sequence': '',
                                        'mrr': '',
                                        'workload': '',
                                        'reference_number': '',
                                        'estimate_url': '',
                                        })

                    aws_details['account_id'] = row[3]
                    aws_details['root_email'] = root_email
                    aws_details['iam_username'] = iam_username
                    aws_details['iam_url'] = iam_url
                    aws_details['payer_account_id'] = row[4]
                    aws_details['reference_number'] = row[0]
                    aws_details['delivery_sequence'] = '000'
                    if aws_order_rec['status'] == 'Not Started':
                        aws_details['allow_order'] = 'No'
                    else:
                        aws_details['allow_order'] = 'Yes'

                    cloud_account = CloudAccounts()
                    cloud_account.customer = customer
                    cloud_account.vendor = VendorDetails.objects.get(pk=1)
                    cloud_account.type = 'AWS'
                    if aws_order_rec['status'] == 'Not Started':
                        cloud_account.active = False
                    else:
                        cloud_account.active = True
                    original_date = row[1].split(' ')
                    try:
                        val = datetime.datetime.strptime(original_date[0], '%d/%m/%y')
                    except ValueError:
                        pass
                    cloud_account.created_at = val
                    cloud_account.created_by = PartnerUserDetails.objects.filter(partner=customer.partner)[0].user
                    cloud_account.details = aws_details
                    cloud_account.modified_by_id = PartnerUserDetails.objects.filter(partner=customer.partner)[
                        0].user.id
                    cloud_account.save()

                    # Insert into pending requests as well
                    pending_request = PendingRequests()
                    pending_request.vendor = cloud_account.vendor
                    pending_request.customer = customer
                    pending_request.partner = customer.partner
                    if aws_order_rec['status'] == 'Not Started':
                        pending_request.active = False
                    else:
                        pending_request.active = True
                    pending_request.cloud_account = cloud_account
                    pending_request.created_by = cloud_account.created_by
                    pending_request.created_at = cloud_account.created_at
                    pending_request.reference_number = row[0]
                    pending_request.save()

                    # Delete from aws_orders
                    del aws_orders[row[0]]

        import pprint
        pprint.pprint("Left Order")
        pprint.pprint(aws_orders)
