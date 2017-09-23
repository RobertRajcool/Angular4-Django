from django.dispatch import receiver
from common.signals import send_mail_notifications
import importlib


@receiver(send_mail_notifications)
def send_mail_on_publish(sender, **kwargs):
    try:
        module = 'common.mails.' + kwargs['trigger']
        mod = importlib.import_module(module)
        instance = eval("mod." + kwargs['trigger'])(kwargs['details'])
        return True
    except Exception:
        mod = importlib.import_module('common.mails.BaseMails')
        instance = eval("mod.BaseMails")(kwargs['details'], kwargs['trigger'])
        return True


def choose_template(trigger):
    template_dict = {
        'PartnerRequest': {
            'html': 'partner_request.html',
            'group': 'partner_request_group.html',
            'sub': 'New Partner Request',
            'cus_sub': 'New Customer Request'
        },
        'PartnerActivation': {
            'html': 'partner_activation.html',
            'group': 'partner_activation_group.html',
            'sub': 'Partner Activation',
            'cus_sub': 'Customer Activation'
        },
        'PartnerRejection': {
            'html': 'partner_rejection.html',
            'group': 'partner_rejection_group.html',
            'sub': 'Partner Rejection',
            'cus_sub': 'Customer Rejection'
        },
        'PartnerRegistration': {
            'html': 'partner_registration.html',
            'group': 'partner_registration_group.html',
            'sub': 'Partner Registration',
            'cus_sub': 'Customer Registration'

        },
        'OrderPlaced': {
            'redington_html': 'order_placed_partner.html',
            'partner_html': 'order_placed_partner.html',
            'sub': 'Order Placed'
        },
        'OrderApproved': {
            'orderapproved_redington_html': 'order_placed_partner.html',
            'orderapproved_partner_html': 'order_approved_partner.html',
            'sub': 'Order Approved'
        },
        'OrderRejected': {
            'order_rejected_redington_html': 'order_placed_partner.html',
            'order_rejected_partner_html': 'order_placed_partner.html',
            'sub': 'Order Rejected'
        },
        'UserCreation': {
            'html': 'user_creation.html',
            'group': 'user_creation_group.html',
            'sub': 'User Creation'
        },
        'ApnidUpdated': {
            'html': 'apn_account_activation.html',
            'sub': 'APN Id Updated'
        },
        'CreditsUpdated': {
            'html': 'aws_credits.html',
            'sub': 'Credits Updated'
        },
        'AwsWindowsPasswordNotification': {
            'html': 'aws_windows_password_notification.html',
            'sub': 'AWS Windows Password Notification'
        },
        'CloudErrorHandling': {
            'partner': 'partner_cloud_error_handling.html',
            'business': 'business_cloud_error_handling.html',
            'technical': 'technical_cloud_error_handling.html',
            'sub': 'Cloud Error Handling'
        },
        'PartnerFeedback': {
            'html': 'partner_feedback_template.html',
            'sub': 'Partner Feedback'
        },
        'AwsAccountLinked': {
            'partner_new_account': 'aws_account_created_and_linked.html',
            'partner_existing_account': 'aws_account_linked.html',
            'sub': 'AWS Account Linked'
        },
        'AccountRequest': {
            'business': 'account_request.html',
            'partner': 'account_request_partner.html',
            'sub': 'Account Request'
        },
        'InstanceProvisioned': {
            'partner': 'instance_provisioned.html',
            'sub': 'Instance Provisioned'
        },
        'InstanceAdded': {
            'html': 'instance_added.html',
            'sub': 'Instance Added'
        },
        'StorageProvisioned': {
            'partner': 'storage_provisioned.html',
            'sub': 'Storage Provisioned'
        },
        'SubscriptionsRenewalAlert': {
            'partner': 'subscription_renewal_alert.html',
            'sub': 'Subscription Renewal Alert'
        },
        'CancelSubscription': {
            'partner_html': 'cancel_subscription_partner.html',
            'redington_html': 'cancel_subscription_redington.html',
            'sub': 'Cancel Subscription'
        },
        'SuspendSubscriptionSuccess': {
            'partner_html': 'cancel_subscription_partner.html',
            'redington_html': 'cancel_subscription_redington.html',
            'sub': 'Suspend Subscription Success'
        },
        'AwsOrdersReport': {
            'redington_html': 'aws_orders_report.html',
            'sub': 'AWS Orders Report'
        },
        'AmendmentAlert': {
            'html': 'amendment_alert.html',
            'sub': 'Amendment Alert'
        },
        'AccountRequestReject': {
            'business': 'account_request_reject.html',
            'partner': 'account_request_partner_reject.html',
            'sub': 'Account Request Reject'
        },
        'AccountRequestApproved': {
            'business': 'account_request_approved.html',
            'partner': 'account_request_partner_approved.html',
            'sub': 'Account Request Approved'
        },
        'RenewalSubscriptionAdvance': {
            'business_html': 'renewal_subscription_advance.html',
            'partner_html': 'renewal_subscription_advance_partner.html',
            'sub': 'Renewal Subscription Advance'
        },
        'AlertDirectSubscriptions': {
            'partner': 'alert_direct_subscriptions.html',
            'sub': 'Alert Direct Subscriptions'
        },
        'DisconnectSubscription': {
            'partner_html': 'disconnect_subscription_partner.html',
            'redington_html': 'disconnect_subscription.html',
            'sub': 'Disconnect Subscriptions'
        },
        'AutoRenewalSubscription': {
            'partner_html': 'auto_renewal_subscription_partner.html',
            'business_html': 'auto_renewal_subscription.html',
            'sub': 'Auto Renewal Subscription'
        },
        'DowngradeSubscriptions': {
            'business_html': 'downgrade_subscriptions.html',
            'sub': 'Downgrade Subscriptions'
        },
        'IsvRegistration': {
            'redington': 'isv_registration_redington.html',
            'html': 'isv_registration.html'

        },
        'IsvRejection': {
            'html': 'isv_rejection.html',
            'sub': 'ISV Rejection',
        },
        'IsvActivation': {
            'html': 'isv_activation.html'
        },
        'RejectIsvProducts': {
            'isv_html': 'reject_isv_product.html',
            'business_html': 'business_reject_isv_product.html'
        },
        'ApproveIsvProducts': {
            'isv_html': 'approve_isv_product.html',
            'business_html': 'business_approve_isv_product.html'
        },
        'IsvServiceRequest': {
            'isv_html': 'isv_service_request.html',
            'business_html': 'business_isv_service_request.html'
        },
        'IsvProductApprovalRequest': {
            'business_html': 'isv_product_approval_request.html'
        },
        'ServiceRequestRejection': {
            'business_html': 'business_reject_service_request.html',

        },
        'ApproveIsvServiceRequest': {
            'isv_html': 'approve_isv_service_request.html',
            'business_html': 'business_approve_service_request.html'
        },
        'PortalTrialRequest': {
            'partner_html': 'portal_partner_trial_request.html',
            'business_html': 'portal_business_trial_request.html'
        },
        'EnquireRequest': {
            'isv_html': 'isv_enquire_request_product.html',
            'business_html': 'business_enquire_request_product.html'
        },
        'AwsSoGenerationFails': {
            'business_html': 'aws_so_generation_fails.html'
        },
        'IsvFeedback': {
            'html': 'isv_feedback_template.html',
            'sub': 'Isv Feedback'
        },
        'IsvTrialAccountRequest': {
            'isv_html': 'isv_trial_account_request.html',
            'business_html': 'business_isv_trial_request.html'
        },

        'ApprovePortalTrialRequest': {
            'partner_html': 'approve_portal_trial_request.html',

        },

    }
    return template_dict[trigger]
