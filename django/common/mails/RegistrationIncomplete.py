from common.mails.BaseMails import BaseMails
from partner.models import InitialContactDetails, InitialPartner
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template


class RegistrationIncomplete(BaseMails):
    def __init__(self, partner_detail):
        self.send_incompletion_mail(partner_detail)
        BaseMails.__init__(self, partner_detail, 'PartnerActivation')

    def send_incompletion_mail(self, detail):
        partner_mail = InitialContactDetails.objects.get(partner=detail['id'], type='P').email
        partner_name = InitialPartner.objects.get(id=detail['id']).preferred_user_name
        subject = 'Partner activation'
        template = choose_template('PartnerActivation')
        from_email = 'cloudsupport@redington.co.in'
        html = get_template(template['html'])
        assigning_values = Context({'username': partner_name})
        html_content = html.render(assigning_values)

        try:
            mail = EmailMessage(subject, html_content, to=[partner_mail], from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)
