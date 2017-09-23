class AppContants:
    DEVELOPER_EMAILS = [
        'redhelpdesk@star-systems.in',
        'cloudsupport@redington.co.in',

    ]
    partner_Type = [
        'Reseller',
        'Consulting & Implementation',
        'Managed Service Provider',
        'Technology Partner'
    ]
    partner_core_business = [
        'Hardware',
        'Software',
        'Services',
        'App Development',
        'Security',
        'Cloud'
    ]
    partner_interested_workLoads = [
        'Website & Web apps',
        'Backup Storage Archive',
        'Disaster Recovery',
        'Hosting',
        'Mailing solution',
        'IT Asset management',
        'Consulting services',
        'Migration Services',
        'Support & Ticketing services',
        'Video conferencing',
        'Customer relationship management',
        'Other Services'
    ]
    partner_focused_customer = [
        'Airlines, Aviation & Defence',
        'Automobile',
        'BFSI',
        'Cement',
        'Marble',
        'Stone Etc',
        'Chemical',
        'Construction',
        'Consulting',
        'Consumer Durables',
        'Home appliances',
        'Courier',
        'Logistics',
        'Packages',
        'E-commerce',
        'Education',
        'Electrical & Electronics',
        'Engineering',
        'Entertainment',
        'Export & Import',
        'Facility Management',
        'FMCG',
        'Agriculture',
        'Hospital',
        'Healthcare',
        'Hospitality',
        'Information Technology',
        'ITES',
        'BPO',
        'KPO',
        'Jewellery',
        'Manufacturing',
        'Marine',
        'NGO',
        'Retail',
        'Service Industry',
        'Telecommunication',
        'Textile',
        'Travel & Tourism'
    ]
    import os
    from django.conf import settings
    AZURE_CUSTOMERS_MONTHLY_BILL_ROOT = os.path.join(settings.MEDIA_ROOT, 'azure_customers_monthly_bill')
    AZURE_CUSTOMERS_MONTHLY_BILL_URL = 'azure_customers_monthly_bill/'
    MS_RENEWAL_BILL_ROOT = os.path.join(settings.MEDIA_ROOT, 'ms_renewal')
    MS_RENEWAL_BILL_URL = 'ms_renewal/'

    DOMAIN_NAME = '127.0.0.1:8000'