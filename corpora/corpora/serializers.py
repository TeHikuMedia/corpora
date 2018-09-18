from django.contrib.auth.models import User, Group
from rest_framework import serializers

import logging
logger = logging.getLogger('corpora')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name')


class UserSerializer(serializers.ModelSerializer):
    # groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ('email', 'pk',)
