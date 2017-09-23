import os.path
import datetime
from redington.settings import AWS_CREDENTIALS, BASE_DIR
from cloudtemplates.runner import EC2Runner
from users.models import RedUser
from partner.models import Partner, ContactDetails
from products.models import VendorDetails
from customers.models import CloudAccounts, Customers
from cloudtemplates.models import RegionDetails, CloudInstances
from cloudtemplates.tasks import get_payer_account
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template
from notifications.models import EmailRecipients, NotificationActions


class AllAwsInstanceDetails:
    """
    This class is used to get all instances from AWS portal based partner customer
    """

    AWS_JBA = 'AWSC'
    playbook = os.path.join(BASE_DIR, 'playbooks', 'aws/get_all_instances.yml')

    def __init__(self, partner):
        """
        This is the initial function of this class
        Through which function only all the actions to be performed
        """
        self.partner = partner  # partner refers to partner id
        self.partner_contact = None
        self.customer = None
        self.instance = None
        self.region = None
        self.recipients = []
        self.html_content = None

    def perform_actions(self):
        """
        Function to set and get all required variables to gather instance details
        :return:
        """
        self.partner = self.get_partner()
        self.partner_contact = self.get_partner_contacts()
        for customer in self.get_aws_customers_account():
            self.customer = customer  # self.customer refers the customer account details object
            print('%s : updating instance details started...' % self.customer.customer.company_name)
            self.handle()

    def handle(self):
        """
        Function to handle the execution of ansible-playbook by sending a customer by each region
        :return:
        """
        for region in self.get_regions():
            self.region = region
            print('%s - %s : updating in progress...' % (self.customer.customer.company_name, region.name))
            try:
                self.run_playbook()
            except Exception:
                # TODO: Need to do exception handling
                print('%s - %s update: exception occurred!' % (self.customer.customer.company_name, region.name))
                continue

    def run_playbook(self):
        """
        Function to execute ansible playbook to get instance details based on customer and region
        :return:
        """
        runner = EC2Runner('Store Output')
        extra_variables = {
            'tenantAccountId': self.customer.details['account_id'],
            'region': self.region.region_id,
        }
        credentials = AWS_CREDENTIALS[get_payer_account(self.customer.customer_id)]
        status, results = runner.get_results(self.playbook, credentials, extra_variables)

        if status:
            self.handle_results(results['instance_facts'])
        else:
            print('%s - %s update: run playbook failed!' % (self.customer.customer.company_name, self.region.name))

    def handle_results(self, result):
        """
        Function to update the gathered instances by region wise
        :param result:
        :return:
        """
        if len(result['instances']) > 0:
            for instance in result['instances']:
                self.instance = instance
                if self.check_instance_exists():
                    self.update_instance()
                    print('%s - Instance updated' % instance['id'])
                else:
                    self.add_instance()
                    self.mail_to_partner()  # Mail notification to partner
                    self.mail_to_business_team()  # Mail notification to business team
                    print('%s - Instance added' % instance['id'])
        else:
            print('No instances available')

    def check_instance_exists(self):
        """,
        Function to check if instance exists for the customer
        :return:
        """
        return CloudInstances.objects.filter(customer_id=self.customer.customer_id, instance_id=self.instance['id'],
                                             region=self.instance['region']).exists()

    def update_instance(self):
        """
        Function to update instance details
        :return:
        """
        ins = CloudInstances.objects.filter(customer_id=self.customer.customer_id, instance_id=self.instance['id'],
                                            region=self.instance['region'])
        ins.update(instance_id=self.instance['id'], state=self.instance['state'],
                   ip_address=self.instance['public_ip_address'], instance_details=self.instance,
                   last_synched_date=datetime.datetime.now())

    def add_instance(self):
        """
        Function to add new instance created via AWS portal
        :return:
        """
        ins = CloudInstances()
        ins.name = self.instance['id']
        ins.instance_id = self.instance['id']
        ins.state = self.instance['state']
        ins.ip_address = self.instance['public_ip_address']
        ins.region = self.instance['region']
        ins.instance_details = self.instance
        ins.security_details = None
        ins.customer_id = self.customer.customer_id
        ins.product_id = 1
        ins.cloudartifact_id = None
        ins.deleted = False
        ins.last_synched_date = datetime.datetime.now()
        ins.save()

        self.instance = ins

    def mail_to_partner(self):
        """
        Function to sending mail alert to partner
        :return:
        """
        subject = 'New AWS instance added in redington portal'
        template = choose_template('InstanceAdded')
        html = get_template(template['html'])
        assigning_values = Context({'instance': self.instance, 'receiver': self.partner_contact.name, 'subject': subject})
        self.html_content = html.render(assigning_values)
        self.recipients = []
        self.recipients = [self.partner_contact.email]
        self.send_mail()

    def mail_to_business_team(self):
        """
        Function to sending mail alert to biz team
        :return:
        """
        subject = 'New AWS instance added in redington portal'
        template = choose_template('SubscriptionsRenewalAlert')
        html = get_template(template['partner'])
        assigning_values = Context({'instance': self.instance, 'receiver': 'Business team', 'subject': subject})
        self.html_content = html.render(assigning_values)
        self.recipients = []
        self.get_business_team()
        self.send_mail()

    def send_mail(self):
        """
        Function to send mail notifications
        :return:
        """
        from_email = 'cloudsupport@redington.co.in'
        subject = 'New AWS instance added in redington portal'
        try:
            mail = EmailMessage(subject, self.html_content, to=self.recipients, from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

        return HttpResponse(True)

    def get_partner(self):
        """
        Function to get the details of partner
        :return:
        """
        return Partner.objects.filter(pk=self.partner).first()

    def get_partner_contacts(self):
        """
        Function to get partner contacts
        :return:
        """
        return ContactDetails.objects.filter(partner_id=self.partner.id, type='P').first()

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

    def get_customers_based_on_partner(self):
        """
        Function to get all customers based on partner
        :return:
        """
        return Customers.objects.filter(partner_id=self.partner.id).values_list('id', flat=True)

    def get_aws_customers_account(self):
        """
        Function to get all aws customers account details
        :return:
        """
        filters = dict()
        filters['customer_id__in'] = self.get_customers_based_on_partner()
        filters['type'] = 'AWS'
        filters['active'] = 1

        return CloudAccounts.objects.filter(**filters)

    def get_regions(self):
        """
        Function to get all the regions available for AWS
        :return:
        """
        return RegionDetails.objects.filter(vendor_id=self.get_aws_vendor())

    def get_aws_vendor(self):
        """
        Function to get AWS vendor id
        :return:
        """
        return VendorDetails.objects.get(vendor_jbareference=self.AWS_JBA).vendor_id
