from common.mails.BaseMails import BaseMails
from partner.models import InitialContactDetails, InitialPartner
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template
from django.conf import settings


class PartnerActivation(BaseMails):
    def __init__(self, partner_detail):
        self.send_activation_mail(partner_detail)
        super(PartnerActivation, self).__init__(partner_detail['partner_detail'], 'PartnerActivation')

    def send_activation_mail(self, detail):
        partner_detail = detail['partner_detail']
        partner = InitialContactDetails.objects.filter(partner=partner_detail['id'], type='P').first()
        subject = 'Customer activation' if partner_detail['customer'] else 'Partner activation'
        template = choose_template('PartnerActivation')
        from_email = 'cloudsupport@redington.co.in'
        html = get_template(template['html'])
        t = 'Customer' if partner_detail['customer'] else 'Partner'
        assigning_values = Context({'username': partner_detail['preferred_user_name'],
                                    'password': detail['password'],
                                    'domain_name': settings.DOMAIN_NAME,
                                    'company_name': partner_detail['company_name'],
                                    'type': t
                                    })
        html_content = html.render(assigning_values)

        try:
            mail = EmailMessage(subject, html_content, to=[partner.email], from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)
