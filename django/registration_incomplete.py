import os
import sys
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context

os.environ['DJANGO_SETTINGS_MODULE'] = 'redington.settings'
application = get_wsgi_application()


def send_incomplete_notification():
    from partner.models import InitialPartner, InitialContactDetails

    subject = 'Registration continue'
    from_email = 'cloudsupport@redington.co.in'
    template = get_template('incomplete.html')
    incomplete_partners = InitialPartner.objects.filter(~Q(registration_status=3)).values('id', 'key')
    for i in incomplete_partners:
        mail_id = InitialContactDetails.objects.filter(Q(partner=i['id']), Q(type='P')).values('email', 'name')
        url = "http://localhost:4200/" + i['key'] + "/registration"
        for mail in mail_id:
            assigning_values = Context({'username': mail['name'], 'url': url})
            html_content = template.render(assigning_values)
            try:
                mail = EmailMessage(subject, html_content, to=[mail['email']], from_email=from_email)
                mail.content_subtype = 'html'
                mail.send(fail_silently=True)
                print('Mail has been sent!')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return HttpResponse(True)


if __name__ == "__main__":
    if sys.argv.__len__() == 1:
        send_incomplete_notification()
