from django.db import models
from datetime import datetime, timedelta
from simple_history.models import HistoricalRecords
from users.models import RedUser
import uuid
class AipDirectory(models.Model):
    office_name = models.CharField(max_length=50)
    pincode = models.CharField(max_length=8)
    office_type = models.CharField(max_length=5)
    delivery_status = models.CharField(max_length=15)
    division = models.CharField(max_length=30)
    region = models.CharField(max_length=30)
    circle = models.CharField(max_length=25)
    taluk = models.CharField(max_length=50)
    district = models.CharField(max_length=30)
    state = models.CharField(max_length=30)

class RedTokens(models.Model):
    table_type = models.IntegerField()
    table_pkid = models.IntegerField()
    token = models.CharField(max_length=255)
    expiry_date = models.DateTimeField(default=datetime.now()+timedelta(days=7))
    status = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    history = HistoricalRecords()

class ConversionRates(models.Model):
    rate = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField()
    history = HistoricalRecords()
class PartnerFeedback(models.Model):
    feedback_number = models.CharField(max_length=25)
    name = models.CharField(max_length=250, default='test')
    email = models.CharField(max_length=250, default='test')
    mobile = models.BigIntegerField(null=False, default=9790584839)
    reason = models.CharField(max_length=250)
    attachment = models.ImageField(upload_to='feedback/%Y-%m-%d-%H-%M-%S')
    description = models.TextField(max_length=1000)
    created_by = models.ForeignKey(RedUser, related_name='feedback')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(RedUser, related_name='feedbackmodified_by', blank=True,
                                            null=True)
    modified_date = models.DateTimeField(blank=True, null=True)