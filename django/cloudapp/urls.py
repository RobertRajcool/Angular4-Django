
from rest_framework import routers
from users.views import UsersViewSet, GroupsViewSet
from common.views import AipDirectoryViewSet, RedTokenViewSet,ConversionRatesViewSet
from notifications.views import NotificationsViewSet, NotificationGroupsViewSet, NotificationActionsViewset
from customers.views import CustomersViewSet, CustomerContactsViewSet, CloudAccountsViewSet, PendingRequestViewSet,\
    MsCustomerViewset
from partner.views import PartnerViewSet, InitialPartnerViewSet, AwsCreditsViewSet, RejectedPartnerViewSet


# Defining Router
cloudapp_router = routers.DefaultRouter()

# Registering ViewSets

cloudapp_router.register(r'users', UsersViewSet)
cloudapp_router.register(r'roles', GroupsViewSet, 'group')
cloudapp_router.register(r'notifications', NotificationsViewSet, 'notifications')
cloudapp_router.register(r'partner_details', PartnerViewSet)
cloudapp_router.register(r'aip-directory', AipDirectoryViewSet, 'aipdirectory')
cloudapp_router.register(r'initial_partner_details', InitialPartnerViewSet)
cloudapp_router.register(r'notification-groups', NotificationGroupsViewSet, 'notificationgroups')
cloudapp_router.register(r'notification-actions', NotificationActionsViewset, 'notificationactions')
cloudapp_router.register(r'customers', CustomersViewSet, 'customers')
cloudapp_router.register(r'customer_contacts', CustomerContactsViewSet)
cloudapp_router.register(r'customer-cloud-accounts', CloudAccountsViewSet, 'cloudaccounts')
cloudapp_router.register(r'token', RedTokenViewSet, '')
cloudapp_router.register(r'pending-requests', PendingRequestViewSet, '')
cloudapp_router.register(r'conversion-rates', ConversionRatesViewSet, 'conversion-rates')
cloudapp_router.register(r'partner-aws-credits', AwsCreditsViewSet)
cloudapp_router.register(r'rejected-partner-details', RejectedPartnerViewSet, 'rejected-partner-details')
cloudapp_router.register(r'ms-customer', MsCustomerViewset, 'ms-customer')

