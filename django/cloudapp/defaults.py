from django.contrib.auth.models import ContentType, Permission


class AppDefaults:
    access_specifiers = None

    @classmethod
    def get_predefined_roles(cls):
        """ Returns predefined role alias and its names """
        return {
            'Admin': 'Predefined/Admin',
            'Partner': 'Predefined/Partner',
            'Customer': 'Predefined/Customer',
            'CreditTeam': 'Predefined/CreditTeam',
            'BusinessTeam': 'Predefined/BusinessTeam',
            'SalesTeam': 'Predefined/SalesTeam',
        }

    @classmethod
    def get_predefined_role_access_specifiers(cls, role_alias):
        """ Returns list of access specifiers for the requesting role alias """
        cls.__init__()

        specifiers_of_predefined_roles = {
            'Admin': list(cls.access_specifiers.keys()),
            # Admin role permission will be added by setting user as superuser
            'Partner': [
                'manage_users',
                'notifications',
                'partners_orders',
                'customers',
                'partner_profile',
                'manage_cloud_accounts'
            ],
            'Customer': [
                'manage_users',
                'notifications',
                'partner_profile',
                'manage_cloud_accounts'
            ],
            'CreditTeam': [
                'view_partner',
                'view_edit_initialpartner'
            ],
            'BusinessTeam': [
                'view_edit_partner',
                'view_customers',
                'manage_cloud_accounts',
                'view_cloud_account_requests',
                'edit_cloud_account_requests',
                'edit_apn_id',
                'customers'
            ],
            'SalesTeam': [
                'view_partner',
                'view_customers',
                'view_cloud_accounts'
            ]
        }
        return specifiers_of_predefined_roles[role_alias]

    @classmethod
    def get_access_specifier_permissions(cls, access):
        """ Returns list of permission ids for the requested access specifier """
        cls.__init__()

        specifier_permissions = []

        if access in cls.access_specifiers.keys():
            specifier_permissions = list(set([item for sublist in cls.access_specifiers[access] for item in sublist]))

        return specifier_permissions, 'permissions'

    @classmethod
    def get_all_permissions(cls, app_label, model):
        """ Returns list of permission ids corresponding to the model """
        return list(
            Permission.objects.filter(content_type__app_label=app_label, content_type__model=model).values_list('id',
                                                                                                                flat=True))

    @classmethod
    def get_permissions(cls, app_label, model_name, codename_list):
        """ Returns list od permission ids of provided code names """
        return list(Permission.objects.filter(content_type__app_label=app_label, content_type__model=model_name,
                                              codename__in=codename_list).values_list('id', flat=True))

    @classmethod
    def get_notification_signals(cls):
        return [
            ('PartnerRequest', 'New partner request'),
            ('PartnerActivation', 'Partner activation'),
            ('PartnerRejection', 'Partner rejection'),
            ('PartnerRegistration', 'Partner registration'),
            ('PartnerFeedback', 'Partner feedback'),
            ('AccountRequest', 'Account request')



        ]

    @classmethod
    def __init__(cls):
        """ Providing values for class variables """

        if cls.access_specifiers is None:
            cls.access_specifiers = {
                'manage_users': [
                    cls.get_all_permissions('users', 'reduser'),
                    cls.get_all_permissions('auth', 'group'),
                    cls.get_all_permissions('users', 'roles')
                ],
                'notifications': [
                    cls.get_all_permissions('notifications', 'notifications')
                ],
                'notifications_groups': [
                    cls.get_all_permissions('notifications', 'notificationgroups'),
                    cls.get_all_permissions('notifications', 'notificationactions')
                ],
                'manage_partners': [
                    cls.get_permissions(app_label='partner', model_name='partner', codename_list=[
                        'list_partner',
                        'view_partner',
                        'add_partner',
                        'change_partner'
                    ]),
                    cls.get_all_permissions('partner', 'contactdetails'),
                    cls.get_all_permissions('partner', 'documentdetails'),
                    cls.get_all_permissions('partner', 'initialpartner'),
                    cls.get_all_permissions('partner', 'initialcontactdetails'),
                    cls.get_all_permissions('partner', 'initialdocumentdetails'),
                ],
                'partner_profile': [
                    cls.get_permissions(app_label='partner', model_name='partner', codename_list=[
                        'view_partner',
                        'change_partner'
                    ]),
                    cls.get_all_permissions('partner', 'contactdetails'),
                    cls.get_permissions(app_label='partner', model_name='documentdetails', codename_list=[
                        'view_documentdetails'
                    ]),
                ],
                'customers': [
                    cls.get_all_permissions('customers', 'customers'),
                    cls.get_all_permissions('customers', 'customercontacts')
                ],
                'view_customers': [
                    cls.get_permissions(app_label='customers', model_name='customers', codename_list=['view_customers'])
                ],
                'view_edit_partner': [
                    cls.get_permissions(app_label='partner', model_name='partner', codename_list=[
                        'list_partner',
                        'view_partner',
                        'change_partner'
                    ]),
                    cls.get_all_permissions('partner', 'contactdetails'),
                    cls.get_permissions(app_label='partner', model_name='documentdetails', codename_list=[
                        'view_documentdetails'
                    ]),
                ],
                'view_partner': [
                    cls.get_permissions(app_label='partner', model_name='partner', codename_list=[
                        'list_partner',
                        'view_partner'
                    ])
                ],
                'view_edit_initialpartner': [
                    cls.get_permissions(app_label='partner', model_name='initialpartner', codename_list=[
                        'list_initialpartner',
                        'view_initialpartner'
                    ])
                ],
                'manage_cloud_accounts': [
                    cls.get_all_permissions(app_label='customers', model='cloudaccounts')
                ],
                'view_cloud_accounts': [
                    cls.get_permissions(app_label='customers', model_name='cloudaccounts', codename_list=[
                        'list_cloudaccounts',
                        'view_cloudaccounts'
                    ])
                ],
                'view_cloud_account_requests': [
                    cls.get_permissions(app_label='customers', model_name='pendingrequests', codename_list=[
                        'list_pendingrequests',
                        'view_pendingrequests'
                    ])
                ],
                'edit_cloud_account_requests': [
                    cls.get_permissions(app_label='customers', model_name='pendingrequests', codename_list=[
                        'change_pendingrequests'
                    ])
                ]

            }

    @classmethod
    def cloud_vendor_codes(cls, return_as=None, query_str=None):
        cloud_vendors = (
            ('MS', 'AZURE'),
            ('AWS', 'AWS'),
            ('SoftLayer', 'SoftLayer')
        )

        if return_as == 'code':
            return cloud_vendors[list(map(lambda x: x[1], cloud_vendors)).index(query_str)][0]
        elif return_as == 'name':
            return cloud_vendors[list(map(lambda x: x[0], cloud_vendors)).index(query_str)][1]
        elif return_as == 'names':
            return [x[1] for x in cloud_vendors]
        elif return_as == 'codes':
            return list(map(lambda x: x[0], cloud_vendors))
        else:
            return cloud_vendors

