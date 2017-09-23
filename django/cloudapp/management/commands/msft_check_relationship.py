from django.core.management import BaseCommand
from customers.models import CloudAccounts, MicrosoftDomains, CustomerContacts, Customers
from customers.microsoft_api import MicrosoftApi
from customers.common_functions import CommonFunctions
from orders.models import Orders
from orders.serializers import OrdersSerializer
from orders.order_approval_steps import MicrosoftOrderProcess


class Command(BaseCommand):
    help = "This command will check whether the customer is came under Redington CSP"

    def handle(self, *args, **options):
        self.check_update_domains()
        print("Getting existing domains")
        domain_query_set = MicrosoftDomains.objects.filter(completed=False)
        domains_list = list(domain_query_set.values())
        connected_count = 0
        if len(domains_list) > 0:
            ms_api = MicrosoftApi()
            print("Number of domains to  check: %d" % len(domains_list))
            for key, record in enumerate(domains_list):
                domain_name = record['domain_name']
                print("Checking domain: %s" % domain_name)
                customer_info = ms_api.get_customer_from_domain(domain_name)
                if 'companyProfile' in customer_info:
                    self.stdout.write(self.style.SUCCESS("Status: connected"))
                    tenant_id = customer_info['companyProfile']['tenantId']
                    cloud_data = CloudAccounts.objects.get(id=record['cloud_account_id'])
                    customer_id = cloud_data.customer_id
                    # Set additional info with the existing data
                    old_data = cloud_data.details
                    old_data['tenant_id'] = tenant_id
                    #old_data['allow_order'] = 'Yes'
                    old_data['active'] = True
                    cloud_data.details = old_data
                    cloud_data.active = True
                    cloud_data.save()

                    CommonFunctions.check_and_complete_request(record['cloud_account_id'])

                    # Check the billing profile is valid
                    billing_info = ms_api.get_customer_billing_info(tenant_id)
                    if billing_info != 'Failed':
                        customer_contact = CustomerContacts.objects.filter(customer_id=customer_id).first()
                        customer = Customers.objects.get(id=customer_id)
                        customer_email = customer_contact.email
                        address = customer.address
                        postcode = customer.Pincode
                        city = customer.city
                        update_mpc = False
                        if billing_info['email'] == '' and customer_email and customer_email != '':
                            billing_info['email'] = customer_email
                            update_mpc = True
                        if billing_info['defaultAddress']['addressLine1'] == '' and address and address != '':
                            billing_info['defaultAddress']['addressLine1'] = address
                            update_mpc = True
                        if billing_info['defaultAddress']['postalCode'] == '' and postcode and postcode != '':
                            billing_info['defaultAddress']['postalCode'] = postcode
                            update_mpc = True
                        if billing_info['defaultAddress']['city'] == '' and city and city != '':
                            billing_info['defaultAddress']['city'] = city
                            update_mpc = True

                        if update_mpc:
                            ms_api.update_billing_info(billing_info, tenant_id)
                    else:
                        print('Failed to get billing profile for domain %s' % domain_name)

                    connected_count += 1
                    # Make the record as completed
                    msd_obj = MicrosoftDomains.objects.get(id=record['id'])
                    msd_obj.completed = True
                    msd_obj.save()
                    self.process_orders(customer_id)
                else:
                    print("Status: Not connected yet")

        self.stdout.write(self.style.SUCCESS('New connection count: %d' % connected_count))


    def process_orders(self, customer_id):
        """
        Function to process the orders approved by business team
        :param customer_id:
        :return:
        """
        from customers.models import Customers
        from partner.models import PartnerUserDetails
        from customers.common_functions import CommonFunctions
        order_id_list = CommonFunctions.get_orders_to_process(customer_id)
        if len(order_id_list):
            customer_object = Customers.objects.get(id=customer_id)
            partner_user = PartnerUserDetails.objects.filter(partner_id=customer_object.partner_id).first()
            order_query = Orders.objects.filter(id__in=order_id_list)
            serializer = OrdersSerializer(order_query, many=True, context={'request': None})
            orders = list(serializer.data)
            ms_process = MicrosoftOrderProcess(None)
            ms_process.initiate_ms_api()
            for index, record in enumerate(orders):
                order_details = record
                vendor_name = order_details['vendor_details']['vendor_name']
                if vendor_name == 'Microsoft' or vendor_name == 'AZURE':
                    is_cloud = True if vendor_name == 'AZURE' else False
                    print('vendor: %s' % vendor_name)
                    print('isCloud: %s' % is_cloud)
                    ms_process.change_order_details(order_details)
                    ms_process.set_is_cloud(is_cloud)
                    test = ms_process.process(partner_user.user_id)
                    print('completed:%s' % test)

    def check_update_domains(self):
        print('Sync domain tables in progress')
        ms_domains = list(MicrosoftDomains.objects.filter(completed=False))
        if len(ms_domains):
            for domain in ms_domains:
                if domain.cloud_account.active:
                    domain.note = 'Completed by cron'
                    domain.completed = True
                    domain.save()

        cloud_accounts = list(CloudAccounts.objects.filter(type='MS', active=False).exclude(details__domain_name=''))
        if len(cloud_accounts):
            for ca in cloud_accounts:
                domain_name = ca.details['domain_name']
                tenant_id = ca.details['tenant_id'] if 'tenant_id' in ca.details else ''
                if tenant_id != '':
                    continue
                print('checking', domain_name)
                ms_domain = list(MicrosoftDomains.objects.filter(cloud_account_id=ca.id))
                if len(ms_domain):
                    domain_object = ms_domain[0]
                    if domain_object.domain_name != domain_name:
                        domain_object.domain_name = domain_name
                        domain_object.note = 'Updated by cron'
                        domain_object.completed = False
                        domain_object.save()
                        print('Domain updated in table')
                else:
                    domain_object = MicrosoftDomains()
                    domain_object.completed = False
                    domain_object.domain_name = domain_name
                    domain_object.cloud_account_id = ca.id
                    domain_object.note = 'Added by cron'
                    domain_object.save()
                    print('Domain added to table')
