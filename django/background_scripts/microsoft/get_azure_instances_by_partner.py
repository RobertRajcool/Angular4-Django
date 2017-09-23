from . import microsoft_base
import requests
import datetime
from cloudtemplates.models import CloudInstances
from partner.models import Partner, ContactDetails
from customers.models import CloudAccounts
from products.models import Products
from orders.models import Subscriptions
from redington.settings import AZURE_CREDENTIALS
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template
from users.models import RedUser
from notifications.models import EmailRecipients, NotificationActions

MSFT_PASSWORD_CLIENT_ID = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'


class GetAzureInstancesByPartner(microsoft_base.MicrosoftBase):

    def __init__(self, partner):
        super(GetAzureInstancesByPartner, self).__init__()
        self.partner = partner
        self.instance = None
        self.recipients = []
        self.html_content = None

    # Main method to get the vm list
    def getVirtualMachines(self):

        customers_cloudaccounts = CloudAccounts.objects.filter(
            type='MS',
            customer__in=Partner.objects.get(pk=self.partner).customers_set.all())

        for cloudaccount in customers_cloudaccounts:
            # Azure
            if 'tenant_id' in cloudaccount.details:
                tenant_id = cloudaccount.details['tenant_id']
                subscription = Subscriptions.objects.filter(customer=cloudaccount.customer, name='Microsoft Azure', status='active')

                if subscription.count() == 0:
                    continue  # TODO: Inform that there is no subscription
                elif not tenant_id:
                    continue  # TODO: Inform that there is no subscription

                login_url = str.format('https://login.windows.net/{}/oauth2/token', tenant_id)
                auth_params = {
                    'grant_type': 'password',
                    'client_id': MSFT_PASSWORD_CLIENT_ID,
                    'scope': 'openid',
                    'resource': 'https://management.azure.com/',
                    'username': AZURE_CREDENTIALS['AZURE_AD_USER'],
                    'password': AZURE_CREDENTIALS['AZURE_PASSWORD']
                }

                auth = requests.post(login_url, auth_params)

                if auth.status_code == 200:
                    auth_json = auth.json()
                    auth_token = auth_json['access_token']

                    subscription_id = subscription[0].subscription
                    all_instances_url = str.format('https://management.azure.com/subscriptions/{}/providers/Microsoft.Compute/virtualmachines',
                                            subscription_id)

                    all_instances_query_params = {
                        'api-version': '2016-04-30-preview'
                    }

                    all_instances = requests.get(all_instances_url, params=all_instances_query_params, headers={
                        'Accept': 'application/json',
                        'Authorization': 'Bearer %s' % (auth_token,)
                    })
                    if all_instances.status_code == 200:
                        instances_out = all_instances.json()
                        instances = instances_out['value']
                        msft_product = Products.objects.get(product_name='Microsoft Azure')
                        for instance in instances:
                            existing_instance = CloudInstances.objects.filter(
                                name=instance['name'],
                                customer=cloudaccount.customer,
                                product=msft_product)

                            if not existing_instance:
                                cloud_instance = CloudInstances()
                                cloud_instance.name = instance['name']
                                cloud_instance.instance_id = instance['name']
                                cloud_instance.state = 'running'
                                cloud_instance.ip_address = 'N/A'
                                cloud_instance.region = instance['location']
                                cloud_instance.instance_details = instance
                                cloud_instance.last_synched_date = datetime.datetime.now()
                                cloud_instance.deleted = 0
                                cloud_instance.customer = cloudaccount.customer
                                cloud_instance.product_id = msft_product.pk
                                cloud_instance.save()

                                self.instance = cloud_instance
                                self.mail_to_partner()  # Mail notification to partner
                                self.mail_to_business_team()  # Mail notification to Business team

    def get_partner_contacts(self):
        """
        Function to get partner contacts
        :return:
        """
        return ContactDetails.objects.filter(partner_id=self.partner, type='P').first()

    def send_mail(self):
        """
        Function to send mail notifications
        :return:
        """
        from_email = 'cloudsupport@redington.co.in'
        subject = 'New Azure instance added in redington portal'
        try:
            mail = EmailMessage(subject, self.html_content, to=self.recipients, from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

        return HttpResponse(True)

    def mail_to_partner(self):
        """
        Function to sending mail alert to partner
        :return:
        """
        partner_contact = self.get_partner_contacts()
        subject = 'New Azure instance added in redington portal'
        template = choose_template('InstanceAdded')
        html = get_template(template['html'])
        assigning_values = Context({'instance': self.instance, 'receiver': partner_contact.name, 'subject': subject})
        self.html_content = html.render(assigning_values)
        self.recipients = []
        self.recipients = [partner_contact.email]
        self.send_mail()

    def mail_to_business_team(self):
        """
        Function to sending mail alert to biz team
        :return:
        """
        subject = 'New Azure instance added in redington portal'
        template = choose_template('SubscriptionsRenewalAlert')
        html = get_template(template['partner'])
        assigning_values = Context({'instance': self.instance, 'receiver': 'Business team', 'subject': subject})
        self.html_content = html.render(assigning_values)
        self.recipients = []
        self.get_business_team()
        self.send_mail()

    def get_business_team(self):
        """
        Function to get business team mail id's
        :return:
        """
        if NotificationActions.objects.filter(action='OrderPlaced').exists():
            nf_actions = NotificationActions.objects.filter(action='OrderPlaced').first()
            if nf_actions:
                for groups in nf_actions.groups.values():
                    for recipient_id in groups['recipients'].split(','):
                        self.recipients.append(RedUser.objects.get(id=int(recipient_id)).email)

                    if EmailRecipients.objects.filter(notification_group=groups['id']).exists():
                        for recipient_mail in list(EmailRecipients.objects.filter(notification_group=groups['id'])):
                            self.recipients.append(recipient_mail.email)

