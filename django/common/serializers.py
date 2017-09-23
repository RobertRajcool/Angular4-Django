from rest_framework import serializers
from common.models import AipDirectory, RedTokens, ConversionRates, PartnerFeedback


class AipDirectorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AipDirectory
        fields = ('url', 'id', 'pincode', 'division', 'region', 'circle', 'taluk', 'district', 'state')


class RedTokenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RedTokens
        fields = ('table_type', 'table_pkid', 'token', 'created_at', 'expiry_date')


class ConversionRatesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ConversionRates
        fields = ('id', 'rate', 'created_at')


class PartnerFeedbackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PartnerFeedback
        fields = ('id', 'reason', 'attachment', 'description')
        read_only_fields = ('created_by', 'modified_by')

    def create(self, validated_data):
        validated_data['created_by'] = validated_data['modified_by'] = self.context['request'].user
        return super(PartnerFeedbackSerializer, self).create(validated_data=validated_data)

    def update(self, instance, validated_data):
        validated_data['modified_by'] = self.context['request'].user
        return super(PartnerFeedbackSerializer, self).update(instance=instance, validated_data=validated_data)