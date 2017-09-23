from common.mails.BaseMails import BaseMails
from common.receivers import choose_template
from notifications.generics.notifications import NfActions
from notifications.models import NotificationGroups
from users.models import RedUser, UserProfileVendorCategory
from partner.models import ContactDetails
import re
from django.db.models import Q
from django.conf import settings


class AccountRequestReject(BaseMails):
    action = 'AccountRequestReject'
    details = {'user': None, 'pending_request': None,'partner': None, 'customer': None,
               'subject': None, 'reject_msg': None, 'reference_number': None
               }

    def __init__(self, details):
        self.details['user'] = details['user']
        self.details['pending_request'] = details['pending_request']
        self.details['partner'] = details['partner']
        self.details['customer'] = details['customer']
        self.details['subject'] = details['subject']
        self.details['discount'] = details['discount']
        self.details['reject_msg'] = details['reject_msg']
        self.notify_to_redington()
        self.notify_to_partner()


    def notify_to_redington(self):
        """ Sending emails & notifications to the respective persons in REDINGTON """

        nf_groups = NotificationGroups.objects.filter(actions__action=self.action)
        non_users_emails = list(nf_groups.values_list('non_user_recipients__email', flat=True))
        sets = list(nf_groups.values_list('recipients', flat=True))
        available_user_ids_in_groups = []
        partner_jbacode = self.details['partner'].jba_code
        partner_jbacode=partner_jbacode.strip()


        if len(sets) > 0:
            user_ids = list(set(UserProfileVendorCategory.objects.filter(Q(location__icontains=partner_jbacode[0:2]) | Q(location='CO')).values_list('user_profile__user__id', flat=True)))
            available_user_ids_in_groups = [user_id for set_string in sets for user_id in set_string.split(',')]
            available_user_ids_in_groups = list(set(available_user_ids_in_groups))
            available_user_ids_in_groups = list(filter(lambda x: re.match(r'[0-9]', x) and int(x) in user_ids, available_user_ids_in_groups))
            available_user_ids_in_groups = RedUser.objects \
                .filter(id__in=available_user_ids_in_groups,
                        profile__vendor_category=self.details['vendor']).values_list('id', flat=True)
            available_user_ids_in_groups = list(map(lambda x: str(x), available_user_ids_in_groups))

            """ Send Notifications """
            if len(available_user_ids_in_groups) > 0:
                NfActions.publish(params={
                    'user': self.details['user'],
                    'nf_type': "message",
                    'recipients': ','.join(available_user_ids_in_groups),
                    'message': "New Account request(%s) rejected" %
                               (self.details['pending_request'].cloud_account.details['reference_number']),
                    'status': "unread",
                    'details_obj': self.details['pending_request']
                })

        users_emails = RedUser.objects.filter(id__in=available_user_ids_in_groups).values_list('email', flat=True)
        users_emails = list(users_emails)

        """ Send Emails """
        if len(users_emails) > 0:
            data = {
                'customer_name': self.details['customer'].company_name,
                'partner_name': self.details['partner'].company_name,
                'reject_msg': self.details['reject_msg']
            }
            BaseMails.send_mail(subject=self.details['subject'],
                                recipients=users_emails + non_users_emails,
                                template_name=choose_template(self.action)['business'],
                                template_data=data)

        return True

    def notify_to_partner(self):
        from partner.models import PartnerUserDetails
        partneruserdetails = PartnerUserDetails.objects.filter(partner=self.details['partner'])
        if len(partneruserdetails) != 0:
            parteruser_id = list(partneruserdetails.values_list('user_id', flat=True))
            NfActions.publish(params={
                'user': self.details['user'],
                'nf_type': "message",
                'recipients': str(parteruser_id[0]),
                'message': "New Account request(%s) rejected" %
                           (self.details['pending_request'].cloud_account.details['reference_number']),
                'status': 'unread',
                'details_obj': self.details['pending_request']
            })
            data = {
                'request_number': self.details['pending_request'].reference_number,
                'discount': self.details['discount'],
                'partner_name': self.details['partner'].company_name,
                'reject_msg': self.details['reject_msg'],
                'customer_name': self.details['customer'].company_name,
            }
            red_user_object = RedUser.objects.filter(id=parteruser_id[0]).first()
            BaseMails.send_mail(subject=self.details['subject'],
                                recipients=[red_user_object.email],
                                template_name=choose_template(self.action)['partner'],
                                template_data=data)

        return True
