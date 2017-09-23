from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import ValidationError


class JsonFieldSerializer(serializers.Serializer):
    def __init__(self, **kwargs):
        self.field = kwargs.pop('field', 'JSON Field')

        """ Defining fields of the serializer """
        for field in kwargs.pop('fields', ()):
            self._declared_fields[field[0]] = field[1]

        super(JsonFieldSerializer, self).__init__(**kwargs)

    def create(self, data):
        fields = self.get_fields()
        rearranged_data = dict()

        for field in fields:
            rearranged_data[field] = data.get(field, None)
            if not rearranged_data[field]:
                rearranged_data[field] = self._declared_fields[field].default \
                    if hasattr(self._declared_fields[field], 'default') \
                       and self._declared_fields[field].default != empty else ''

        self.initial_data = rearranged_data
        self.is_valid(raise_exception=True)

        return self._validated_data

    def update(self, instance_data, data):
        fields = self.get_fields()
        rearranged_data = dict()

        for field in fields:
            if self.partial:
                rearranged_data[field] = data.get(field, instance_data[field])
            else:
                rearranged_data[field] = data.get(field, None)

            if not rearranged_data[field]:
                rearranged_data[field] = self._declared_fields[field].default \
                    if hasattr(self._declared_fields[field], 'default') \
                       and self._declared_fields[field].default != empty else ''

        self.initial_data = rearranged_data
        self.is_valid(raise_exception=True)

        return self._validated_data

    def perform_create(self):
        self.create(data=self.initial_data)

    def perform_update(self, instance_data):
        self.update(instance_data=instance_data, data=self.initial_data)

    def is_valid(self, raise_exception=False):
        return super(JsonFieldSerializer, self).is_valid(raise_exception=raise_exception)

    def validate(self, attrs):
        return super(JsonFieldSerializer, self).validate(attrs=attrs)

    def run_validation(self, data=empty):
        """ Formatting Error details """
        try:
            return super(JsonFieldSerializer, self).run_validation(data=data)
        except ValidationError as exc:
            raise ValidationError({self.field: exc})
