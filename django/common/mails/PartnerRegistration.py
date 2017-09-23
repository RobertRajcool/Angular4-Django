from common.mails.BaseMails import BaseMails
from partner.models import InitialContactDetails
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template


class PartnerRegistration(BaseMails):
    def __init__(self, partner_detail):
        self.send_partner_registration_mail(partner_detail)
        super(PartnerRegistration, self).__init__(partner_detail['partner_detail'], 'PartnerRegistration')

    def send_partner_registration_mail(self, partner_detail):
        detail = partner_detail['partner_detail']
        partner = InitialContactDetails.objects.filter(partner=detail['id'], type='P').first()
        subject = 'Customer registration' if detail['customer'] else 'Partner registration'
        t = 'Customer' if detail['customer'] else 'Partner'
        template = choose_template('PartnerRegistration')
        from_email = 'cloudsupport@redington.co.in'
        html = get_template(template['html'])
        assigning_values = Context({'username': partner.name, 'url': partner_detail['url'], 'type': t})
        html_content = html.render(assigning_values)

        try:
            mail = EmailMessage(subject, html_content, to=[partner.email], from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)
