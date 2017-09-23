import datetime
from orders.models import Subscriptions
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template
from customers.models import CustomerContacts
from partner.models import ContactDetails
from users.models import RedUser
from notifications.models import EmailRecipients, NotificationActions


class SubscriptionsRenewalNotifications:
    """
    This class used to send notifications to Biz team and partner about Subscription renewal
    Notifications will send before 3rd day of renewal date
    """

    def __init__(self):
        """
        This is the initial function of this class
        Through which function only all the actions to be performed
        """
        self.subscriptions = None  # All subscriptions
        self.subscription = None  # Current subscription
        self.customer = None
        self.partner = None
        self.recipients = []
        self.html_content = None
        self.date = None
        self.end_date = None
        self.days = None

    def perform_actions(self):
        """
        Function to set and get all values which required to sending notifications
        :return:
        """
        self.get_subscriptions()
        self.date = datetime.date.today()

    def check_subscriptions(self):
        """
        Function to check subscription renewal date
        :return:
        """
        for subscription in list(self.subscriptions):
            self.subscription = subscription
            self.end_date = self.subscription.commitment_end_date.date().strftime('%Y-%m-%d')
            self.get_customer_contacts()
            self.get_partner_contacts()
            self.days = self.subscription.commitment_end_date.date() - self.date
            if self.days and self.days.days <= 3:
                self.mail_to_customer()
                self.mail_to_partner()
                self.mail_to_business_team()

    def mail_to_customer(self):
        """
        Function to sending mail alert to partner
        :return:
        """
        subject = 'Subscription renewal alert'
        template = choose_template('SubscriptionsRenewalAlert')
        html = get_template(template['partner'])
        assigning_values = Context({'subscription': self.subscription, 'days': self.days.days, 'subject': subject,
                                    'end_date': self.end_date, 'receiver': 'customer'})
        self.html_content = html.render(assigning_values)
        self.recipients = [self.customer.email]
        self.send_mail()

    def mail_to_partner(self):
        """
        Function to sending mail alert to partner
        :return:
        """
        subject = 'Subscription renewal alert'
        template = choose_template('SubscriptionsRenewalAlert')
        html = get_template(template['partner'])
        assigning_values = Context({'subscription': self.subscription, 'days': self.days.days, 'subject': subject,
                                    'end_date': self.end_date, 'receiver': self.partner.name})
        self.html_content = html.render(assigning_values)
        self.recipients = []
        self.recipients = [self.partner.email]
        self.send_mail()

    def mail_to_business_team(self):
        """
        Function to sending mail alert to biz team
        :return:
        """
        subject = 'Subscription renewal alert'
        template = choose_template('SubscriptionsRenewalAlert')
        html = get_template(template['partner'])
        assigning_values = Context({'subscription': self.subscription, 'days': self.days.days, 'subject': subject,
                                    'end_date': self.end_date, 'receiver': 'Business team'})
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
        subject = 'Subscription renewal alert'
        try:
            mail = EmailMessage(subject, self.html_content, to=self.recipients, from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

        return HttpResponse(True)

    def get_subscriptions(self):
        """
        Function to get all subscriptions of O365
        :return:
        """
        self.subscriptions = Subscriptions.objects.filter(billing_type='license', status='active')

    def get_customer_contacts(self):
        """
        Function to get customer contacts based on subscription
        :return:
        """
        self.customer = CustomerContacts.objects.filter(customer_id=self.subscription.customer_id).first()

    def get_partner_contacts(self):
        """
        Function to get partner contacts based on subscription
        :return:
        """
        self.partner = ContactDetails.objects.filter(partner_id=self.subscription.customer.partner_id, type='P').first()

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
