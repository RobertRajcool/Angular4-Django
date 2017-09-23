from django.db.models import Q
from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from partner.models import InitialPartner, InitialContactDetails


class PartnerRegistrationIncomplete:
    def __init__(self):
        """
        This is the constructor of this class
        """

    def perform_actions(self):
        """
        Function to perform actions to send notification mails to registration incomplete partners
        :return:
        """
        for partner in self.get_incomplete_partners():
            url = settings.DOMAIN_NAME + '/' + partner.key + "/registration"
            self.send_mail(url=url, partner=self.get_partner_contact_details(partner.id))

    def send_mail(self, url, partner):
        """
        Function to send notification mails
        url is string which refers to the portal partner registration URL
        partner is dict which refers to the partner contact details
        :param url:
        :param partner:
        :return:
        """
        subject = 'Registration continue'
        from_email = 'cloudsupport@redington.co.in'
        template = get_template('partner_incomplete_registration.html')
        assigning_values = Context({'username': partner.name, 'url': url})
        html_content = template.render(assigning_values)

        try:
            mail = EmailMessage(subject, html_content, to=[partner.email], from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
            print('Mail has been sent to %s!' % partner.name)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)

    def get_partner_contact_details(self, partner):
        """
        Function to get partner contact details
        partner is number which refers to the partner id
        :param partner:
        :return:
        """
        return InitialContactDetails.objects.filter(Q(partner=partner), Q(type='P')).first()

    def get_incomplete_partners(self):
        """
        Function to get registration incomplete partners list
        :return:
        """
        return InitialPartner.objects.filter(~Q(registration_status=3))