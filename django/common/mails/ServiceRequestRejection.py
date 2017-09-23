from common.mails.BaseMails import BaseMails
from django.template import Context
from common.receivers import choose_template
from notifications.generics.notifications import NfActions
from notifications.models import NotificationGroups
from users.models import RedUser



class ServiceRequestRejection(BaseMails):
    action = 'ServiceRequestRejection'
    details = {'user': None, 'isv_details': None, 'isv_marketplace_service_instance': None}
    template_data = {'username': None, 'rejection_reason ': None, 'isv_detail': None}

    def __init__(self, details):
        self.details['user'] = details['user']
        self.details['isv_details'] = details['service_details']
        self.details['rejection_reason'] = details['rejection_reason']
        self.details['isv_marketplace_service_instance'] = details['isv_marketplace_service_instance']
        self.template_data['isv_detail'] = details['service_details']['isv_service']
        self.template_data['username'] = details['service_details']['isv']['company_name']
        self.template_data['rejection_reason']=details['rejection_reason']
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
                    'user': RedUser.objects.filter(is_superuser=True).first(),
                    'nf_type': "message",
                    'recipients': nf_recipients,
                    'message': "Reject ISV Service Request: %s" %
                               (
                                   self.details['rejection_reason']
                               ),
                    'status': "unread",
                    'details_obj': self.details['isv_marketplace_service_instance']
                })
        users_emails = RedUser.objects.filter(id__in=available_user_ids_in_groups).values_list('email', flat=True)
        users_emails = list(users_emails)
        recipients = users_emails + non_users_emails
        """ Send Emails """
        subject = 'Service Request Rejected: %s ' % (self.template_data['isv_detail']['service_name'])
        if len(recipients) > 0:
            BaseMails.send_mail(subject=subject,
                                recipients=recipients,
                                template_name=choose_template(self.action)['business_html'],
                                template_data=self.template_data
                                )

    def notify_to_respects(self):
        subject = 'Service Request Rejected'
        BaseMails.send_mail(subject=subject,
                            recipients=[self.details['isv_details']['isv']['contacts'][0]['email']],
                            template_name=choose_template(self.action)['business_html'],
                            template_data=self.template_data
                            )
        return True

