from django.contrib.auth.models import User, Group
from rest_framework import serializers

import logging
logger = logging.getLogger('corpora')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'pk',)

    def create(self, validated_data):
        try:
            user, created = User.objects.get_or_create(**validated_data)
        except Exception as e:
            raise Exception(e)
        return user
