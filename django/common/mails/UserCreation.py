from common.mails.BaseMails import BaseMails
from partner.models import InitialContactDetails, InitialPartner
from users.models import RedUser
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template
from django.conf import settings


class UserCreation(BaseMails):
    def __init__(self, user_detail):
        self.send_creation_mail(user_detail)
        BaseMails.__init__(self, user_detail['user_detail'], 'UserCreation')

    def send_creation_mail(self, detail):
        user_detail = detail['user_detail']
        user_obj = RedUser.objects.filter(pk=user_detail['id']).values().first()
        user_mail = user_obj['email']
        user_name = user_obj['username']
        first_name = user_obj['first_name']
        last_name = user_obj['last_name']
        subject = 'User creation'
        template = choose_template('UserCreation')
        from_email = 'cloudsupport@redington.co.in'
        html = get_template(template['html'])
        assigning_values = Context({'username': user_name, 'password': detail['password'],
                                    'firstname': first_name, 'lastname': last_name, 'domain_name': settings.DOMAIN_NAME})
        html_content = html.render(assigning_values)

        try:
            mail = EmailMessage(subject, html_content, to=[user_mail], from_email=from_email)
            mail.content_subtype = 'html'
            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)
