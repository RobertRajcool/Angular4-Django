from django.db import models
from users.models import RedUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_comma_separated_integer_list
from cloudapp.defaults import AppDefaults
from simple_history.models import HistoricalRecords


class Notifications(models.Model):
    type = models.CharField(max_length=1, choices=(('A', 'Alert'), ('M', 'Message')))
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    details = GenericForeignKey('content_type', 'object_id')
    recipients = models.CharField(max_length=200, validators=[validate_comma_separated_integer_list])
    purpose = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=15)
    posted_by = models.ForeignKey(RedUser, related_name='notification_posted')
    posted_at = models.DateTimeField(auto_now_add=True)
    viewed_by = models.CharField(max_length=50, validators=[validate_comma_separated_integer_list], null=True)
    completed_by = models.ForeignKey(RedUser, related_name='notification_completed', null=True)
    completed_at = models.DateTimeField(null=True)
    history = HistoricalRecords()


class NotificationGroups(models.Model):
    name = models.CharField(max_length=30)
    recipients = models.TextField(validators=[validate_comma_separated_integer_list], null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(RedUser, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(RedUser, related_name="+")
    modified_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(RedUser, related_name="+", null=True)
    history = HistoricalRecords()


class EmailRecipients(models.Model):
    notification_group = models.ForeignKey(NotificationGroups, related_name='non_user_recipients')
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=70)
    created_by = models.ForeignKey(RedUser, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(RedUser, related_name="+")
    modified_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


class NotificationActions(models.Model):
    action = models.CharField(max_length=50, choices=AppDefaults.get_notification_signals())
    groups = models.ManyToManyField(NotificationGroups, related_name='actions')
    created_by = models.ForeignKey(RedUser, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(RedUser, related_name="+")
    modified_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
