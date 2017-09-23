from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from simple_history.models import HistoricalRecords

class RedUser(AbstractUser):
    pass


USER_TYPE_CHOICES = (
    ('R', 'Redington'),
    ('P', 'Partner'),
    ('C', 'Customer'),
    ('I', 'ISV'),
    ('RI', 'ISV Manager')
)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    user_type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES)
    address = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=100, null=True)
    user_location = models.CharField(max_length=50, null=True)
    password_change_date = models.DateTimeField(null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='modified_by', blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    role_id = models.CharField(max_length=100, validators=[validate_comma_separated_integer_list], null=True)
    history = HistoricalRecords()


class Roles(models.Model):
    group = models.OneToOneField(Group, related_name='details', on_delete=models.CASCADE)
    alias = models.CharField(max_length=50)
    created_by = models.ForeignKey(RedUser, to_field='id', null=True)
    accesses = models.TextField(null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ('view_customer_products_report', 'Can view customer view report'),
            ('view_cloud_billing_report', 'Can view cloud bill report'),
            ('view_saas_business_report', 'can view saas business report'),
            ('view_saas_sales_report', 'can view saassalesreport'),
            ('view_product_report', 'can view product saas report'),
            ('view_overall_sales_report', 'can view overall sales report'),
            ('view_zone_wise_report', 'can view zone wise sales report'),
            ('view_order_report', 'can view order report')
        )

class PasswordResetTokens(models.Model):
    user = models.ForeignKey(RedUser, related_name="+")
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserProfileVendorCategory(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    location = models.CharField(max_length=256)