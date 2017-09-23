from common.mails.BaseMails import BaseMails
from common.receivers import choose_template
from notifications.generics.notifications import NfActions
from notifications.models import NotificationGroups
from users.models import RedUser
from django.conf import settings

class PartnerFeedback(BaseMails):
    action = 'PartnerFeedback'
    details = {'user': None, 'feedback_details': None}
    template_data = {'username': None, 'feedback_number': None}

    def __init__(self, details):
        self.details['user'] = details['user']
        self.details['feedback_details'] = details['feedback_details']
        self.template_data['username'] = details['user'].username
        self.template_data['feedback_number'] = details['feedback_details'].feedback_number
        self.template_data['feedback'] = details['feedback_details'].reason
        self.template_data['mobile'] = details['feedback_details'].mobile
        self.template_data['email'] = details['feedback_details'].email
        self.template_data['description'] = details['feedback_details'].description
        self.notify_to_redington()
        self.notify_to_respects()

    def notify_to_redington(self):
        nf_groups = NotificationGroups.objects.filter(actions__action=self.action).exclude(recipients='')
        non_users_emails = list(nf_groups.values_list('non_user_recipients__email', flat=True))
        sets = list(nf_groups.values_list('recipients', flat=True))
        available_user_ids_in_groups = []

        if len(sets) > 0:
            available_user_ids_in_groups = [user_id for set_string in sets for user_id in set_string.split(',')]
            available_user_ids_in_groups = list(set(available_user_ids_in_groups))

            available_user_ids_in_groups = list(map(lambda x: str(x), available_user_ids_in_groups))

            """ Send Notifications """
            if len(available_user_ids_in_groups) > 0:
                nf_recipients = ','.join(available_user_ids_in_groups)
                NfActions.publish(params={
                    'user': self.details['user'],
                    'nf_type': "message",
                    'recipients': nf_recipients,
                    'message': "Partner Support",
                    'status': "unread",
                    'details_obj': self.details['feedback_details']
                })

        users_emails = RedUser.objects.filter(id__in=available_user_ids_in_groups).values_list('email', flat=True)
        users_emails = list(users_emails)
        from cloudapp.generics.constant import AppContants
        recipients = users_emails + non_users_emails+AppContants.DEVELOPER_EMAILS
        subject = 'Support from Partner: '+ self.details['feedback_details'].reason
        """ Send Emails """
        if len(recipients) > 0:
            if self.details['feedback_details'].attachment.name != '':
                import magic
                mime = magic.Magic(mime=True)
                attachements_url = self.details['feedback_details'].attachment.url
                file_extension = mime.from_file(settings.BASE_DIR + '/' + attachements_url)
                attchements = dict()
                attchements['url'] = attachements_url
                attchements['extenstions'] = file_extension
                BaseMails.send_mail(subject=subject,
                                    recipients=recipients,
                                    template_name=choose_template(self.action)['html'],
                                    template_data=self.template_data,
                                    attachements=attchements
                                    )
            else:
                BaseMails.send_mail(subject=subject,
                                    recipients=recipients,
                                    template_name=choose_template(self.action)['html'],
                                    template_data=self.template_data
                                    )

    def notify_to_respects(self):
        """ Sending emails & notifications to the respective persons for the order """

        """ Publishing Notifications """
        nf_recipients = ','.join([str(self.details['user'].id)])
        NfActions.publish(params={
            'user': self.details['user'],
            'nf_type': "message",
            'recipients': nf_recipients,
            'message': "Support Tracking Id: " + self.template_data['feedback_number'],
            'status': 'unread',
            'details_obj': self.details['feedback_details']
        })
        return True