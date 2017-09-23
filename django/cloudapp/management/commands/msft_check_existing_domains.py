from django.core.management import BaseCommand
from customers.models import CloudAccounts
from customers.microsoft_api import MicrosoftApi


class Command(BaseCommand):
    help = "This command will check whether the customer is came under Redington CSP"

    def handle(self, *args, **options):
        partner_id = int(options['options'][0])
        print("Getting existing domains for partner id: %d" % partner_id)
        self.check_existing_domains(partner_id)

        self.stdout.write(self.style.SUCCESS('Process completed'))

    def check_existing_domains(self, partner_id):
        """
        Function to check the existing domains are valid
        :return:
        """
        cloud_data = CloudAccounts.objects.filter(type='MS', active=True, customer__partner_id=partner_id).values()
        if len(cloud_data):
            from users.get_users import GetUsers
            ms_api = MicrosoftApi()
            users_object = GetUsers()
            # Get users associated to Microsoft
            ms_users = users_object.get_users_given_vendor_name('Microsoft', 'email')
            # Get users associated to AZURE
            azure_users = users_object.get_users_given_vendor_name('AZURE', 'email')
            biz_users = ms_users + azure_users
            domains = []
            for record in cloud_data:
                details = record['details']
                domain_name = details['domain_name']
                print(domain_name)
                if domain_name and domain_name != '':
                    customer_info = ms_api.get_customer_from_domain(domain_name)
                    # To handle invalid domains
                    if 'companyProfile' not in customer_info:
                        print('Invalid')
                        cloud_data = CloudAccounts.objects.get(id=record['id'])
                        cloud_data.active = False
                        cloud_data.save()
                        domains.append(domain_name)
                        print('set as inactive')
                    else:
                        print('valid')
            if len(domains) and len(biz_users):
                domain_names = ','.join(domains)
                message = 'Please check the following accounts in Microsoft were become invalid: ' + domain_names
                data = {'subject': 'Account expired', 'message': message}
                # Send mail to the business team
                self.send_mail_to_business_team(biz_users, data)

    def send_mail_to_business_team(self, to, data):
        """
        Function to send mail to the business team
        :param data:
        :return:
        """
        from common.mails.BaseMails import BaseMails
        BaseMails.send_mail(subject=data['subject'],
                            recipients=to,
                            template_name='plain.html',
                            template_data={'message': data['message']})

        return True
