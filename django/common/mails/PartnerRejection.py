from common.mails.BaseMails import BaseMails
from partner.models import InitialContactDetails
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template
import socket


class PartnerRejection(BaseMails):
    def __init__(self, partner_detail):
        self.send_partner_rejection_mail(partner_detail)
        super(PartnerRejection, self).__init__(partner_detail['partner_detail'], 'PartnerRejection')

    def send_partner_rejection_mail(self, detail):
        partner_detail = detail['partner_detail']
        rejection_reason = detail['rejection_reason']
        partner = InitialContactDetails.objects.filter(partner=partner_detail['id'], type='P').first()
        subject = 'Customer activation rejected' if partner_detail['customer'] else 'Partner activation rejected'
        t = 'Customer' if partner_detail['customer'] else 'Partner'
        template = choose_template('PartnerRejection')
        from_email = 'cloudsupport@redington.co.in'
        html = get_template(template['html'])
        assigning_values = Context({'username': partner.name, 'rejection_reason': rejection_reason, 'url': detail['url'],
                                    'type': t})
        html_content = html.render(assigning_values)

        try:
            mail = EmailMessage(subject, html_content, to=[partner.email], from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)
