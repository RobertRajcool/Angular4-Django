from notifications.models import EmailRecipients, NotificationActions
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from common.receivers import choose_template
from partner.models import InitialPartner
from django.conf import settings
from notifications.models import NotificationGroups
from users.models import RedUser, UserProfileVendorCategory
import re
from django.db.models import Q


class BaseMails:
    redington_recipients = {
        'user_ids': [],
        'emails': []
    }

    def __init__(self, data, trigger):
        self.send_on_action(data, trigger)

    @classmethod
    def send_on_action(self, data, trigger):
        if NotificationActions.objects.filter(action=trigger).exists():
            notification_groups = NotificationActions.objects.get(action=trigger) \
                .groups.values('id', 'recipients', 'non_user_recipients')
            recipients_email_array = []
            company = InitialPartner.objects.get(pk=data['id']).company_name
            template_data = dict()
            template_data['partner_details'] = data
            template_data['contact_details'] = data['initial_contacts']
            template_data['username'] = company
            template_data['type'] = 'Customer' if data['customer'] else 'Partner'
            sub = choose_template(trigger=trigger)['cus_sub'] if data['customer'] else \
                choose_template(trigger=trigger)['sub']
            for group in notification_groups:
                group_id = group['id']
                recipients_str = group['recipients']
                recipients_arr = recipients_str.split(',')

                for recipients in recipients_arr:
                    recipients_email_array.append(RedUser.objects.get(id=int(recipients)).email)

                    if EmailRecipients.objects.filter(notification_group=group_id).exists():
                        for mail in EmailRecipients.objects.filter(notification_group=group_id).values("email"):
                            recipients_email_array.append(mail['email'])

            BaseMails.send_mail(subject=sub, recipients=recipients_email_array,
                                template_name=choose_template(trigger)['group'],
                                template_data=template_data)
        else:
            return HttpResponse(True)

    @classmethod
    def send_mail(cls, subject, recipients, template_name, template_data, attachements=None,
                  attachments_full_path=None, data_attachments=list(), cc_to=[]):
        """" Sends email for the provided details """
        '''Attachment is Optional Parameters. Attachements should be dist its contains url and extenstions'''

        from_email = 'cloudsupport@redington.co.in'
        html = get_template(template_name)
        assigning_values = Context(template_data)
        html_content = html.render(assigning_values)
        if recipients and len(recipients) > 0:
            recipients = list(set(recipients))
            if None in recipients:
                recipients.remove(None)

        try:
            mail = EmailMessage(subject, html_content, to=recipients, from_email=from_email, cc=cc_to)
            mail.content_subtype = 'html'
            if attachements is not None:
                mail.attach_file(settings.BASE_DIR + '/' + attachements['url'], attachements['extenstions'])
            elif attachments_full_path is not None:
                mail.attach_file(attachments_full_path)

            """ Attaching data as files into email """
            for attachment in data_attachments:
                mail.attach(filename=attachment['filename'],
                            content=attachment['content'].decode('utf-8'),
                            mimetype=attachment['mimetype'])

            mail.send(fail_silently=True)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse(True)

    def query_redington_users(self, actions=[], vendor_id=None, partner_location=None):
        """ Querying redington recipients for the notification action """

        for action in actions:
            emails = list()
            ids = list()
            nf_groups = NotificationGroups.objects.filter(actions__action=action)
            emails += list(nf_groups.values_list('non_user_recipients__email', flat=True))
            sets = list(nf_groups.values_list('recipients', flat=True))

            if len(sets) > 0:
                user_ids = list(set(UserProfileVendorCategory.objects.filter(
                    Q(location__icontains=partner_location) | Q(location='CO')).values_list('user_profile__user__id',
                                                                                                  flat=True)))
                available_user_ids_in_groups = [user_id for set_string in sets for user_id in set_string.split(',')]
                available_user_ids_in_groups = list(set(available_user_ids_in_groups))
                available_user_ids_in_groups = list(
                    filter(lambda x: re.match(r'[0-9]', x) and int(x) in user_ids, available_user_ids_in_groups))
                available_user_ids_in_groups = RedUser.objects \
                    .filter(id__in=available_user_ids_in_groups,
                            profile__vendor_category__pk=vendor_id) \
                    .values_list('id', flat=True)

                ids.append(list(map(lambda x: str(x), available_user_ids_in_groups)))

                users_emails = RedUser.objects.filter(id__in=ids).values_list('email', flat=True)
                emails += list(users_emails)

                self.redington_recipients['emails'] = emails
                self.redington_recipients['user_ids'] = ids
