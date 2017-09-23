from rest_framework import serializers
from django.db.models.functions import Concat
from django.db.models import Value
from notifications.models import Notifications, NotificationGroups, EmailRecipients, NotificationActions
from users.serializers import UsersSerializer, GroupSerializer
from users.models import RedUser
from customers.serializers import CloudAccountsSerializer
from common.serializers import PartnerFeedbackSerializer


class NotificationsSerializer(serializers.HyperlinkedModelSerializer):
    subject = serializers.CharField(source='content_type.model', read_only=True)

    def to_representation(self, instance):
        """ Serialize GenericForeignKey field """

        primitive_repr = super(NotificationsSerializer, self).to_representation(instance)

        if 'details' in primitive_repr and instance.details is not None:
            serializer_maps = {
                'RedUser': (UsersSerializer, 'Users'),
                'Group': (GroupSerializer, 'Roles'),
                'CloudAccounts': (CloudAccountsSerializer, 'CloudAccounts'),
                'PartnerFeedback': (PartnerFeedbackSerializer, 'PartnerFeedback')
            }

            if instance.details._meta.model.__name__ in serializer_maps.keys():
                primitive_repr['subject'] = serializer_maps[instance.details._meta.model.__name__][1]
                primitive_repr['details'] = serializer_maps[instance.details._meta.model.__name__][0] \
                    (instance.details, context={'request': self.context['request']}).data
            else:
                primitive_repr['subject'] = primitive_repr['details'] = None

        return primitive_repr

    class Meta:
        model = Notifications
        fields = ('url', 'id', 'type', 'subject', 'details', 'recipients', 'purpose',
                  'status', 'posted_by', 'posted_at', 'viewed_by', 'completed_by', 'completed_at')
        read_only_fields = ['posted_at']


class EmailRecipientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailRecipients
        fields = ('id', 'name', 'email')


class NotificationGroupsSerializer(serializers.HyperlinkedModelSerializer):
    non_user_recipients = EmailRecipientsSerializer(many=True, allow_null=True)

    def to_representation(self, instance):
        """ Serialize comma separated primary keys field """

        primitive_repr = super(NotificationGroupsSerializer, self).to_representation(instance)
        if 'recipients' in primitive_repr and instance.recipients is not None and instance.recipients != '':
            """ Reconstruct recipients details """
            primary_keys = primitive_repr['recipients'].split(',')
            primitive_repr['recipients'] = list(
                RedUser.objects.filter(id__in=primary_keys).extra(select={'text': 'CONCAT(`first_name`, " ", `last_name`)'}).values('id', 'text'))

        return primitive_repr

    class Meta:
        model = NotificationGroups
        fields = (
            'url', 'id', 'name', 'recipients', 'non_user_recipients', 'description', 'created_by',
            'created_at', 'modified_by', 'modified_at')
        read_only_fields = ('created_by', 'modified_by')

    def create(self, validated_data):
        validated_data['created_by'] = validated_data['modified_by'] = self.context['request'].user
        non_users_recipients_list = validated_data['non_user_recipients']
        validated_data.pop('non_user_recipients')
        instance = super(NotificationGroupsSerializer, self).create(validated_data)
        self.create_or_update_non_user_recipients(instance, non_users_recipients_list)
        return instance

    def update(self, instance, validated_data):
        validated_data['modified_by'] = self.context['request'].user
        self.create_or_update_non_user_recipients(instance, validated_data['non_user_recipients'])
        validated_data.pop('non_user_recipients')
        return super(NotificationGroupsSerializer, self).update(instance, validated_data)

    def create_or_update_non_user_recipients(self, instance, recipients_list):
        """ Create , Update, Delete EmailRecipients """
        existing_list = EmailRecipients.objects.filter(notification_group_id=instance.id)
        new_list = []
        if recipients_list is not None:
            for rcpt in recipients_list:

                if rcpt is not None and 'id' in rcpt.keys():
                    matched_list = existing_list.filter(id=rcpt['id'])
                    if len(matched_list) > 0:
                        matched_list[0].__dict__.update(**rcpt)
                        matched_list[0].modified_by = self.context['request'].user
                        matched_list[0].save()
                        new_list.append(matched_list[0].id)

                else:
                    rcpt['notification_group'] = instance
                    rcpt['created_by'] = rcpt['modified_by'] = self.context['request'].user
                    email_rcpt = EmailRecipients.objects.create(**rcpt)
                    email_rcpt.save()
                    new_list.append(email_rcpt.id)

            deleted_list = existing_list.exclude(id__in=new_list)
            deleted_list.delete()


class NotificationActionsSerializer(serializers.ModelSerializer):
    groups = NotificationGroupsSerializer(many=True)

    class Meta:
        model = NotificationActions
        fields = ('url', 'id', 'action', 'groups', 'created_by', 'created_at', 'modified_by', 'modified_by')
        read_only_fields = ('created_by', 'modified_by')

    def create(self, validated_data):
        validated_data['created_by'] = validated_data['modified_by'] = self.context['request'].user
        return super(NotificationActionsSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data['modified_by'] = self.context['request'].user
        return super(NotificationActionsSerializer, self).update(instance, validated_data)
