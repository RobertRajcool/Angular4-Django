from common.mails.BaseMails import BaseMails
from partner.models import InitialContactDetails
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template


class PartnerRequest(BaseMails):
    def __init__(self, partner_detail):
        self.send_partner_request_mail(partner_detail)
        super(PartnerRequest, self).__init__(partner_detail, 'PartnerRequest')

    def send_partner_request_mail(self, detail):
        partner = InitialContactDetails.objects.filter(partner=detail['id'], type='P').first()
        subject = 'Customer registration completed' if detail['customer'] else 'Partner registration completed'
        t = 'Customer' if detail['customer'] else 'Partner'
        template = choose_template('PartnerRequest')
        from_email = 'cloudsupport@redington.co.in'
        html = get_template(template['html'])
        assigning_values = Context({'username': partner.name, 'type': t})
        html_content = html.render(assigning_values)

        try:
            mail = EmailMessage(subject, html_content, to=[partner.email], from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)
