from rest_framework import serializers
from partner.models import Partner, InitialPartner, ContactDetails, DocumentDetails, \
    InitialContactDetails, InitialDocumentDetails, AwsCredits, HistoricalRecords, PartnerUserDetails, PartnerRating


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactDetails
        fields = ('id', 'type', 'name', 'email', 'mobile')


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentDetails
        fields = ('id', 'type', 'file_name', 'file_data')


class PartnerSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        """  """
        primitive_repr = super(PartnerSerializer, self).to_representation(instance=instance)
        partner = instance.id
        partner_user_obj = PartnerUserDetails.objects.filter(partner_id=partner).first()

        primitive_repr['user_name'] = partner_user_obj.user.username if partner_user_obj else None
        if instance.customer:
            primitive_repr['orc_link_code'] = Partner.objects.filter(pk=instance.partner).first().jba_code if \
                instance.partner else None

        return primitive_repr

    class Meta:
        model = Partner
        fields = ('id', 'company_name', 'status', 'jba_code', 'credits', 'vendor_list', 'address_1', 'address_2',
                  'address_3', 'city', 'state', 'pin_code', 'partner_type', 'business_type', 'focused_customer',
                  'credits', 'interested_workload', 'created_at', 'updated_at', 'activated_by', 'contacts', 'documents',
                  'existing_status', 'mpn_id', 'apn_id', 'apn_id_active', 'gst_number', 'customer', 'activated_at',
                  'partner')


class InitialContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialContactDetails
        fields = ('id', 'type', 'name', 'email', 'mobile')


class InitialDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialDocumentDetails
        fields = ('id', 'type', 'file_name', 'file_data')


class InitialPartnerSerializer(serializers.ModelSerializer):
    initial_contacts = InitialContactSerializer(many=True, read_only=True)
    initial_documents = InitialDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = InitialPartner
        fields = ('id', 'key', 'company_name', 'status', 'jba_code', 'credits', 'vendor_list', 'address_1', 'address_2',
                  'address_3', 'city', 'state', 'pin_code', 'partner_type', 'business_type', 'focused_customer',
                  'interested_workload', 'created_at', 'updated_at', 'activated_by', 'activated_at', 'initial_contacts',
                  'initial_documents', 'preferred_user_name', 'registration_status', 'existing_status', 'gst_number',
                  'customer')


class AwsCreditsSerializer(serializers.ModelSerializer):
    expiry_date = serializers.DateTimeField()
    partner_details = PartnerSerializer(source='partner', read_only=True)

    class Meta:
        model = AwsCredits
        fields = ('id', 'coupon_code', 'value', 'expiry_date', 'created_by', 'created_date', 'modified_by', 'modified_date', 'customer', 'partner_details')


class PartnerRatingSerializer(serializers.ModelSerializer):
    partner_details = PartnerSerializer(source='partner', read_only=True)
    created_date = serializers.DateTimeField(format="%b %d,%Y")

    class Meta:
        model = PartnerRating
        fields = ('id', 'rating', 'feedback', 'partner_details', 'created_date')
