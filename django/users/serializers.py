import datetime

from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from rest_framework import serializers

from cloudapp.defaults import AppDefaults
from users.models import RedUser, USER_TYPE_CHOICES, UserProfile, Roles, UserProfileVendorCategory

from partner.models import Partner, PartnerUserDetails


class UsersSerializer(serializers.HyperlinkedModelSerializer):
    address = serializers.CharField(source='profile.address', max_length=255, allow_null=True, allow_blank=True)
    description = serializers.CharField(source='profile.description', max_length=100, allow_null=True, allow_blank=True)
    user_type = serializers.ChoiceField(source='profile.user_type', choices=USER_TYPE_CHOICES)
    user_location = serializers.CharField(source='profile.user_location', max_length=100, allow_null=True, allow_blank=True)
    permissions = serializers.ListField(source='get_all_permissions', read_only=True)
    role_id = serializers.CharField(source='profile.role_id', max_length=100, allow_null=True)

    def to_representation(self, instance):
        """ Serialize GenericForeignKey field """

        primitive_repr = super(UsersSerializer, self).to_representation(instance)

        if 'first_name' in primitive_repr and 'last_name' in primitive_repr:
            primitive_repr['full_name'] = '%s %s' %(primitive_repr['first_name'],primitive_repr['last_name'])

        return primitive_repr

    class Meta:
        model = RedUser
        fields = ('url', 'id', 'username', 'first_name', 'last_name', 'email', 'address', 'description', 'user_type',
                  'user_location','permissions', 'role_id', 'is_superuser')

    # def __init__(self, *args, **kwargs):
    #     super(UsersSerializer, self).__init__(*args, **kwargs)
    #     if 'view' not in self.context.keys():
    #         self.fields.pop('permissions')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        user = super(UsersSerializer, self).create(validated_data)
        user.set_password('123456')
        user.save()
        profile_data['created_by'] = self.context['request'].user
        self.create_or_update_profile(user, profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        profile_data['modified_by'] = self.context['request'].user
        profile_data['modified_date'] = datetime.datetime.now()
        self.create_or_update_profile(instance, profile_data)
        return super(UsersSerializer, self).update(instance, validated_data)

    def create_or_update_profile(self, user, profile_data):
        profile, created = UserProfile.objects.get_or_create(user=user, defaults=profile_data)
        if not created and profile_data is not None:
            super(UsersSerializer, self).update(profile, profile_data)

        permission_groups = Group.objects.filter(id__in=profile_data['role_id'].split(','))

        if permission_groups.filter(name="Predefined/Admin").exists():
            user.is_superuser = True
            user.save()
        else:
            user.is_superuser = False
            user.groups = permission_groups
            user.save()

        partner_userDetails = PartnerUserDetails.objects.filter(user=user.id).exists()
        if not partner_userDetails and profile.user_type == 'P':
            partner_user_obj = PartnerUserDetails()
            partner_id = PartnerUserDetails.objects.get(user=self.context['request']._user.id).partner_id
            partner_user_obj.partner = Partner.objects.get(id=partner_id)
            partner_user_obj.user = RedUser.objects.get(id=user.id)
            partner_user_obj.save()


        vendorids =self.context['request']._data['vendor_category']
        region_name=self.context['request']._data['region_name']
        if vendorids != '':
            i=0;
            location_data=region_name[i]
            data_region_split=",".join(location_data)
            for vendorid in vendorids.split(','):
                if location_data!='CO':
                   vendor_obj = UserProfileVendorCategory(user_profile=profile, location=data_region_split)
                   vendor_obj.save()
                   i+=1
                else:
                    vendor_obj = UserProfileVendorCategory(user_profile=profile, location=location_data)
                    vendor_obj.save()
                    i += 1


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    alias = serializers.CharField(source='details.alias', max_length=50)
    created_by = serializers.CharField(source='details.created_by', read_only=True)
    accesses = serializers.CharField(source='details.accesses', allow_null=True)
    description = serializers.CharField(source='details.description', allow_null=True)
    created_at = serializers.DateTimeField(source='details.created_at', read_only=True)
    modified_at = serializers.DateTimeField(source='details.modified_at', read_only=True)

    class Meta:
        model = Group
        fields = ('url', 'id', 'name', 'alias', 'accesses', 'created_by', 'description', 'created_at', 'modified_at')
        read_only_fields = ['name']

    def create(self, validated_data):
        details_data = validated_data.pop('details', None)
        # Defining Group name
        if self.context['request'].user.is_superuser and details_data['alias'] in AppDefaults.get_predefined_roles().keys():
            validated_data['name'] = AppDefaults.get_predefined_roles()[details_data['alias']]
        else:
            validated_data['name'] = self.context['request'].user.username + '/' + details_data['alias']

        group = super(GroupSerializer, self).create(validated_data)
        group.save()
        details_data['created_by'] = self.context['request'].user
        details_data['created_at'] = datetime.datetime.now()
        details_data['modified_at'] = datetime.datetime.now()
        self.create_or_update_details(group, details_data)
        group = self.add_or_update_permissions(group, details_data['accesses'])
        return group

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        # Defining Group name
        if 'alias' in details_data.keys():
            if self.context['request'].user.is_superuser and details_data['alias'] in AppDefaults.get_predefined_roles().keys():
                validated_data['name'] = AppDefaults.get_predefined_roles()[details_data['alias']]
            else:
                validated_data['name'] = self.context['request'].user.username + '/' + details_data['alias']

        details_data['modified_at'] = datetime.datetime.now()
        self.create_or_update_details(instance, details_data)
        instance = self.add_or_update_permissions(instance, details_data['accesses'])
        return super(GroupSerializer, self).update(instance, validated_data)

    def create_or_update_details(self, group, details_data):
        details, created = Roles.objects.get_or_create(group=group, defaults=details_data)
        if not created and details_data is not None:
            super(GroupSerializer, self).update(details, details_data)

    def add_or_update_permissions(self, group, accesses):
        allowed_permissions = []

        if accesses is not None:
            permitted_accesses = accesses.split(',')
            content_types_list = []
            permissions_list = []
            for access in permitted_accesses:
                array, permission_level = AppDefaults.get_access_specifier_permissions(access)
                if permission_level == 'content_types':
                    content_types_list += array
                elif permission_level == 'permissions':
                    permissions_list += array
            allowed_permissions = Permission.objects.filter(
                Q(id__in=permissions_list) | Q(content_type__in=content_types_list))

        group.permissions = allowed_permissions
        return group
