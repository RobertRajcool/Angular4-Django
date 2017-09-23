from django.db import models
from users.models import RedUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_comma_separated_integer_list
from django.conf import settings
from simple_history.models import HistoricalRecords

PARTNER_TYPE_CHOICES = (
    ('R', 'Reseller'),
    ('C&I', 'Consulting & Implementation'),
    ('MSP', 'Managed Service Provider'),
    ('TP', 'Technology Partner')
)

PARTNER_BUSINESS_TYPE_CHOICES = (
    ('H/W', 'Hardware'),
    ('S/W', 'Software'),
    ('S', 'Services'),
    ('AD', 'App Development'),
    ('Sec', 'Security'),
    ('C', 'Cloud')
)

CONTACT_TYPE_CHOICES = (
    ('P', 'Primary'),
    ('D/O', 'Director/Owner'),
    ('A&O', 'A/c Person & Operation Executive'),
    ('S', 'Sales Person'),
    ('O', 'Others')
)

DOCUMENT_TYPE_CHOICES = (
    ('Bank statement', 'Last 3 months bank statement'),
    ('Audits', 'Latest Audit Accounts with Income Tax return acknowledgement copy'),
    ('CST & LST', 'CST & LST Registration proof'),
    ('Memorandum & Articles', 'Memorandum & Articles of Association/Partnership Agreements'),
    ('Passport', 'Copy of Passport of Properitor/Partner/Directors'),
    ('Pan card', 'Company Pan Card'),
    ('Service tax', 'Service tax Certificate')
)


class Partner(models.Model):
    customer = models.BooleanField(default=False)
    partner = models.IntegerField(default=None, null=True)
    company_name = models.CharField(max_length=75)
    status = models.BooleanField()
    existing_status = models.BooleanField()
    jba_code = models.CharField(max_length=35, null=True)
    gst_number = models.CharField(max_length=25, default=None, null=True)
    credits = models.CharField(max_length=12)
    vendor_list = models.CharField(max_length=75)
    address_1 = models.CharField(max_length=125)
    address_2 = models.CharField(max_length=125, null=True)
    address_3 = models.CharField(max_length=75, null=True)
    city = models.CharField(max_length=35, null=True)
    state = models.CharField(max_length=35, null=True)
    pin_code = models.CharField(max_length=12, null=True)
    partner_type = models.CharField(max_length=25, choices=PARTNER_TYPE_CHOICES)
    business_type = models.CharField(max_length=35, choices=PARTNER_BUSINESS_TYPE_CHOICES)
    focused_customer = models.CharField(max_length=255, validators=[validate_comma_separated_integer_list], null=True)
    interested_workload = models.CharField(max_length=255, validators=[validate_comma_separated_integer_list], null=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    activated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="+")
    activated_at = models.DateField(auto_now_add=True, editable=False, null=True)
    mpn_id = models.CharField(max_length=20, null=True)
    apn_id = models.CharField(max_length=20, null=True)
    apn_id_active = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ('change_mpnid', 'Can change MPN ID'),
            ('change_apnid', 'Can change APN ID')
        )


class ContactDetails(models.Model):
    partner = models.ForeignKey(Partner, related_name='contacts', on_delete=models.CASCADE)
    type = models.CharField(max_length=5, choices=CONTACT_TYPE_CHOICES)
    name = models.CharField(max_length=55)
    email = models.EmailField(max_length=100, null=True)
    mobile = models.CharField(max_length=50)
    history = HistoricalRecords()


class DocumentDetails(models.Model):
    partner = models.ForeignKey(Partner, related_name='documents', on_delete=models.CASCADE)
    type = models.CharField(max_length=35, choices=DOCUMENT_TYPE_CHOICES)
    file_name = models.CharField(max_length=75)
    file_data = models.FileField()


class PartnerUserDetails(models.Model):
    partner = models.ForeignKey(Partner, related_name='users', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='partner', null=True)


class InitialPartner(models.Model):
    key = models.CharField(max_length=32)
    customer = models.BooleanField(default=False)
    registration_status = models.IntegerField(null=True)
    preferred_user_name = models.CharField(max_length=75)
    gst_number = models.CharField(max_length=25, default=None, null=True)
    company_name = models.CharField(max_length=75, null=True)
    status = models.BooleanField()
    existing_status = models.BooleanField()
    jba_code = models.CharField(max_length=35, null=True)
    credits = models.CharField(max_length=12, null=True)
    vendor_list = models.CharField(max_length=75, null=True)
    address_1 = models.CharField(max_length=125, null=True)
    address_2 = models.CharField(max_length=125, null=True)
    address_3 = models.CharField(max_length=75, null=True)
    city = models.CharField(max_length=35, null=True)
    state = models.CharField(max_length=35, null=True)
    pin_code = models.CharField(max_length=12, null=True)
    partner_type = models.CharField(max_length=25, choices=PARTNER_TYPE_CHOICES)
    business_type = models.CharField(max_length=35, choices=PARTNER_BUSINESS_TYPE_CHOICES)
    focused_customer = models.CharField(max_length=255, validators=[validate_comma_separated_integer_list], null=True)
    interested_workload = models.CharField(max_length=255, validators=[validate_comma_separated_integer_list], null=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    activated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    activated_at = models.DateField(auto_now_add=True, editable=False, null=True)


class InitialContactDetails(models.Model):
    partner = models.ForeignKey(InitialPartner, related_name='initial_contacts', on_delete=models.CASCADE)
    type = models.CharField(max_length=5, choices=CONTACT_TYPE_CHOICES)
    name = models.CharField(max_length=55, null=True)
    email = models.EmailField(max_length=100, null=True)
    mobile = models.CharField(max_length=15, null=True)


class InitialDocumentDetails(models.Model):
    partner = models.ForeignKey(InitialPartner, related_name='initial_documents', on_delete=models.CASCADE)
    type = models.CharField(max_length=35, choices=DOCUMENT_TYPE_CHOICES)
    file_name = models.CharField(max_length=75)
    file_data = models.FileField(upload_to='documents/%Y-%m-%d:%H-%M-%S', blank=True, null=True)


class PartnerRejections(models.Model):
    partner = models.ForeignKey(InitialPartner, related_name='partner_rejections', on_delete=models.CASCADE)
    rejection_reason = models.TextField(null=True)
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    rejected_at = models.DateField(auto_now_add=True, editable=False, null=True)


class AwsCredits(models.Model):
    partner = models.ForeignKey(Partner, related_name='aws_credits', on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=55)
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    customer = models.IntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_date = models.DateTimeField()
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()


class PartnerRating(models.Model):
    partner = models.ForeignKey(Partner, related_name='partner_rating', on_delete=models.CASCADE)
    rating = models.CharField(max_length=10)
    feedback = models.TextField()
    created_date = models.DateField(auto_now_add=True, editable=False)

