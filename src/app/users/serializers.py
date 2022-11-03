from rest_framework import serializers
from django.contrib.auth.models import User


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )

    def create(self, validated_data):
        # override standard method to create customer using put method
        validated_data['id'] = self.context['request'].id
        return super(AccountSerializer, self).create(validated_data)
