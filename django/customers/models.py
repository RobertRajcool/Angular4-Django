from django.db import models
from users.models import RedUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from simple_history.models import HistoricalRecords
from partner.models import Partner
from django_mysql.models import JSONField
from cloudapp.defaults import AppDefaults
from django.core.validators import validate_comma_separated_integer_list


class Customers(models.Model):
    partner = models.ForeignKey(Partner)
    company_name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='vendors/%Y-%m-%d-%H-%M-%S')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    Pincode = models.CharField(max_length=100)
    pan_number = models.CharField(max_length=20)
    deleted = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True, editable=False)
    customer_vertical = models.CharField(max_length=75, validators=[validate_comma_separated_integer_list], null=True)
    delivery_sequence=models.CharField(max_length=75)
    segment = models.CharField(max_length=100)
    history = HistoricalRecords()


class CustomerContacts(models.Model):
    customer = models.ForeignKey(Customers,related_name='contacts')
    name = models.CharField(max_length=100, null=True)
    position = models.CharField(max_length=150, null=True)
    email = models.EmailField(max_length=100, null=True)
    mobile = models.CharField(max_length=50, null=True)
    history = HistoricalRecords()


class CloudAccounts(models.Model):
    ACCOUNT_TYPES = AppDefaults.cloud_vendor_codes()

    customer = models.ForeignKey(Customers, related_name='cloud_accounts')
    type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)
    details = JSONField(default=None)
    licenses_and_credentials = JSONField(default=None, null=True, blank=True)
    active = models.BooleanField(default=False)
    created_by = models.ForeignKey(RedUser, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(RedUser, related_name="+")
    modified_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def get_account_type_value(self, label=None):
        """ Obtaining Account type key for given label """
        if label is not None:
            index = list(map(lambda x: x[1], self.ACCOUNT_TYPES)).index(label)
            return self.ACCOUNT_TYPES[index][0]
        else:
            return None


class MicrosoftDomains(models.Model):
    domain_name = models.CharField(max_length=255)
    cloud_account = models.ForeignKey(CloudAccounts)
    completed = models.BooleanField(default=False)
    note = models.CharField(max_length=20, blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()


class PendingRequests(models.Model):
    customer = models.ForeignKey(Customers, related_name='+')
    partner = models.ForeignKey(Partner, related_name='+')
    active = models.BooleanField(default=False)
    cloud_account = models.ForeignKey(CloudAccounts, related_name='+')
    created_by = models.ForeignKey(RedUser, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=30)

