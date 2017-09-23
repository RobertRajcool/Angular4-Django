from rest_framework import serializers
from customers.models import Customers, CustomerContacts, CloudAccounts, PendingRequests
from cloudapp.generics.hashers import AESCipher
from cloudapp.defaults import AppDefaults
from background_scripts.jba.jba_webservice import JBAWebService
from customers import form_data
from partner.serializers import PartnerSerializer


class CustomerContactsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomerContacts
        fields = ('id', 'name', 'position', 'email', 'mobile')


class CustomersSerializer(serializers.ModelSerializer):
    contacts = CustomerContactsSerializer(many=True, read_only=True)
    partner_name = serializers.CharField(source='partner.company_name', read_only=True)

    class Meta:
        model = Customers
        fields = (
            'id', 'company_name', 'logo', 'address', 'city', 'state', 'country', 'pan_number', 'contacts', 'partner',
            'partner_name', 'customer_vertical', 'Pincode', 'created_at')


class CloudAccountsSerializer(serializers.ModelSerializer):
    details = serializers.JSONField(allow_null=True)
    customer_details = CustomersSerializer(source='customer', read_only=True)

    def to_representation(self, instance):
        """ Reformatting values """

        premitive_repr = super(CloudAccountsSerializer, self).to_representation(instance)
        query_params = self.context['request'].query_params.dict()

        if premitive_repr['type'] == 'AWS' and \
                premitive_repr['details'] and 'iam_password' in premitive_repr['details'] and \
                (premitive_repr['details']['iam_password'] is not None):

            if 'decrypt_passwords' in query_params and query_params['decrypt_passwords']:
                cipher = AESCipher()
                premitive_repr['details']['iam_password'] = cipher.decrypt(
                    premitive_repr['details']['iam_password'].encode())
            else:
                premitive_repr['details']['iam_password'] = "%s" % '*' * 6

        premitive_repr['details'] = self.format_details(account_type=premitive_repr['type'],
                                                        details=premitive_repr['details'])

        # Fetching supportive data
        if 'form_data' in query_params and query_params['form_data']:
            # For AWS
            if instance.type == 'AWS':
                # Fetching delivery sequences for

                partners_jba_code = instance.customer.partner.jba_code
                delivery_sequences, st_code = JBAWebService().fetch_partner_delivery_sequence(
                    partner_jba_code=partners_jba_code)
                if st_code != 200:
                    raise ConnectionRefusedError(delivery_sequences)

                premitive_repr['delivery_sequences'] = delivery_sequences
                premitive_repr['workload_choices'] = form_data.AWS_WORKLOADS
        if instance.active:
            premitive_repr['active_status'] = 'Yes'
        else:
            premitive_repr['active_status'] = 'No'

        return premitive_repr

    class Meta:
        model = CloudAccounts
        fields = ('url', 'id', 'customer', 'customer_details', 'active', 'type', 'details',
                  'licenses_and_credentials', 'created_by', 'created_at', 'modified_by', 'modified_at')
        read_only_fields = ('created_by', 'modified_by')

    def create(self, validated_data):
        validated_data = self.update_hidden_fields(validated_data=validated_data)

        return super(CloudAccountsSerializer, self).create(validated_data=validated_data)

    def update(self, instance, validated_data):
        validated_data = self.update_hidden_fields(validated_data=validated_data, instance=instance)

        return super(CloudAccountsSerializer, self).update(instance=instance, validated_data=validated_data)

    def format_details(self, account_type, details=None):
        """ Formats None values into '' on JSON field """
        details_interface = dict()
        if account_type == 'AWS':
            details_interface = {'iam_username': '', 'payer_account_id': '', 'iam_url': '',
                                 'iam_password': '', 'friendly_name': '', 'account_id': '',
                                 'delivery_sequence': '', 'mrr': '', 'workload': '','reference_number': '',
                                 'estimate_url': '', 'root_email': '', 'account_name': ''}
        elif account_type == 'MS':
            details_interface = {'domain_name': '', 'tenant_id': '', 'reference_number': ''}

        details_interface.update(details) if details is not None else details

        return {key: '' if not value else value for key, value in
                details_interface.items()}

    def update_hidden_fields(self, validated_data, instance=None):
        validated_data['modified_by'] = self.context['request'].user

        if not instance:
            validated_data['created_by'] = self.context['request'].user

        # Password formatting
        if 'iam_password' in validated_data['details'] and validated_data['details']['iam_password'] is not None:
            cipher = AESCipher()
            validated_data['details']['iam_password'] = cipher.encrypt(
                validated_data['details']['iam_password']).decode()

        # Defining allow_order
        cloud_vendor_codes = AppDefaults.cloud_vendor_codes(return_as="codes")
        account_type = validated_data.get('type', None)

        if not account_type and instance is not None:
            account_type = AppDefaults.cloud_vendor_codes(return_as="code", query_str=instance.vendor.vendor_name)

        if account_type in cloud_vendor_codes:
            validated_data['details']['allow_order'] = "Yes" if validated_data['active'] else "No"

        return validated_data


class PendingRequestsSerializer(serializers.ModelSerializer):
    customer_details = CustomersSerializer(source='customer', read_only=True)
    cloud_account_details = CloudAccountsSerializer(source='cloud_account', read_only=True)
    partner_details = PartnerSerializer(source='partner', read_only=True)

    class Meta:
        model = PendingRequests
        fields = ('id', 'customer_details', 'cloud_account_details', 'partner',
                  'active', 'created_at', 'reference_number', 'partner_details')
