
import requests
import datetime
import os
import json
from redington import settings
from django.core.management import BaseCommand
import csv
from customers.models import Customers, CloudAccounts
from partner.models import PartnerUserDetails
from products.models import VendorDetails

from background_scripts.microsoft.microsoft_base import MicrosoftBase

class Command(BaseCommand):
    help = "This command migrates Microsoft domain names"

    def handle(self, *args, **options):
        migration_csvs = os.path.join(settings.BASE_DIR, 'migrations')

        microsoft_customers = '/tmp/customers.json'
        existing_microsoft_domains = os.path.join(migration_csvs, 'microsoft_domains.csv')

        #m = MicrosoftBase()
        #headers = m.getAccessHeaders()
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6InowMzl6ZHNGdWl6cEJmQlZLMVRuMjVRSFlPMCIsImtpZCI6InowMzl6ZHNGdWl6cEJmQlZLMVRuMjVRSFlPMCJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLndpbmRvd3MubmV0IiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvN2MyNjFhMTktM2VmZS00ZTZjLTg5ZGEtZDBlNmVhOTc0MzZkLyIsImlhdCI6MTQ5NTA2NzI5NSwibmJmIjoxNDk1MDY3Mjk1LCJleHAiOjE0OTUwNzExOTUsImFpbyI6IlkyWmdZUGoxNzdyVGZaRkQwblBtbk5mNE1PSFFXd0E9IiwiYXBwaWQiOiI5MzFhYTEzNy1mOGQ4LTQ3ZWMtYjZmNS04Y2ZlNzQ5ZWEyOGEiLCJhcHBpZGFjciI6IjEiLCJpZHAiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83YzI2MWExOS0zZWZlLTRlNmMtODlkYS1kMGU2ZWE5NzQzNmQvIiwib2lkIjoiODk5YTg4NTUtMWU0Mi00OTVkLThlOTEtOGI0ODFkYTc3M2JkIiwicm9sZXMiOlsiRGlyZWN0b3J5LlJlYWQuQWxsIiwiRGlyZWN0b3J5LlJlYWRXcml0ZS5BbGwiLCJEb21haW4uUmVhZFdyaXRlLkFsbCJdLCJzdWIiOiI4OTlhODg1NS0xZTQyLTQ5NWQtOGU5MS04YjQ4MWRhNzczYmQiLCJ0aWQiOiI3YzI2MWExOS0zZWZlLTRlNmMtODlkYS1kMGU2ZWE5NzQzNmQiLCJ1dGkiOiJoNm4xUmVRZndVU3k1WXdMNVdnT0FBIiwidmVyIjoiMS4wIn0.GJpCvBwXpByxlGHlCV734u8tONCv9KFwLuheTGJ4dXb1J__4DV0fhlTFu902v9Ew3nckd2NpPNOwkk49jmGHIsoe2Etmo6KMDyOzVF3oQmUAiYSNl-RBkj4eUZ1hgRuCapMN6SeGOtJ8dNoP1park-Lx-NMV9QA-pVUZmLJ9HyvREwFhn3lIXL7kYhKbeuf6NN5UUwytvLMBirWGt4d4YnGHhMuJ5SfytmlEKxwAE5pzeIBlCg8C2U8zt-bu2rJuAJ4dhF80Y8HFEzz6j1atje1qbyVcTNxsOeKZ7I1HArTEk90RsFEs0MwJmuURq6J-xUYe4urgry4i3Z41hYE2FA',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        customers = json.load(open('/tmp/customer_map.json', 'r'))

        # Map onmicrosoft.com domain to tenantId
        domain_id_maps = {}
        with open(existing_microsoft_domains, 'r', encoding='latin1') as csvfile:
            for row in reversed(list(csv.reader(csvfile))):
                if row[1]:
                    customer = None
                    try:
                        customer = Customers.objects.get(pk=customers[row[4]])
                    except KeyError:
                        print("Coudlnt find Customer for %s" % (row[4],))
                        continue

                    cloud_account_exists = CloudAccounts.objects.filter(
                        customer = customer,
                        vendor=VendorDetails.objects.get(pk=4),
                        type = 'MS'
                    )
                    if cloud_account_exists:
                        continue        # Already processed

                    full_domain = str.strip(row[1])
                    if full_domain.find('.') == -1:
                        full_domain = str.format('{}.onmicrosoft.com', full_domain)

                    partner_center_url = 'https://api.partnercenter.microsoft.com/v1/customers?filter={"Field":"Domain","Value":"%s","Operator":"starts_with"}' % full_domain
                    domain_request = requests.get(partner_center_url, headers=headers)
                    domain_request.encoding = 'utf-8-sig'
                    if domain_request.status_code != 200:
                        print("Error getting domains for %s " %(full_domain))
                        continue

                    data_to_send = customer_data = json.loads(domain_request.text)
                    result = customer_data['items']
                    if len(result):
                        data_to_send = result[0]
                        tenant_id = data_to_send['id']

                        cloud_account = CloudAccounts()
                        cloud_account.customer = customer
                        cloud_account.vendor = VendorDetails.objects.get(pk=4)        # Hardcode to O365
                        cloud_account.type = 'MS'
                        cloud_account.active = True
                        original_date = row[5].split(' ')
                        try:
                            val = datetime.datetime.strptime(original_date[0], '%d/%m/%y')
                        except ValueError:
                            pass
                        cloud_account.created_at = val
                        cloud_account.created_by = PartnerUserDetails.objects.filter(partner = customer.partner)[0].user
                        cloud_account.details = {
                            'active': True,
                            'domain_name': full_domain,
                            'tenant_id': tenant_id,
                            'allow_order': 'Yes'
                        }
                        cloud_account.active = True
                        cloud_account.modified_by_id = PartnerUserDetails.objects.filter(partner = customer.partner)[0].user.id
                        cloud_account.save()

                    else:
                        # Domain invalid
                        if not row[4] in customers:
                            print("Domain %s invalid, invalid customer" %(full_domain,))
                            continue
                        else:
                            print("domain: %s invalid for customer: %s" %(full_domain, Customers.objects.get(pk=customers[row[4]]).company_name))
                        customer = None
                        try:
                            customer = Customers.objects.get(pk=customers[row[4]])
                        except KeyError:
                            print("Coudlnt find Customer for %s" %(row[4],))
                            continue

                        customer = Customers.objects.get(pk=customers[row[4]])
                        cloud_account = CloudAccounts()
                        cloud_account.customer = customer
                        cloud_account.vendor = VendorDetails.objects.get(pk=4)  # Hardcode to O365
                        cloud_account.type = 'MS'
                        cloud_account.active = False
                        original_date = row[5].split(' ')
                        val = None
                        try:
                            val = datetime.datetime.strptime(original_date[0], '%d/%m/%y')
                        except ValueError:
                            pass
                        cloud_account.created_at = val
                        cloud_account.created_by = PartnerUserDetails.objects.filter(partner=customer.partner)[0].user
                        cloud_account.details = {
                            'domain_name': full_domain,
                            'allow_order': 'No'
                        }
                        cloud_account.modified_by_id = PartnerUserDetails.objects.filter(partner=customer.partner)[0].user.id
                        cloud_account.save()
                else:
                    print("Cannot find domain for %s" %(row[0],))
