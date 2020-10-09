from people.models import \
    Person, Tribe, Demographic, KnownLanguage, Group
from django.contrib.auth.models import User

from corpora.serializers import UserSerializer
from rest_framework import serializers
from dal import autocomplete

import ast
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from allauth.account.models import EmailAddress

import logging
logger = logging.getLogger('corpora')


class TribeSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Tribe model. Note that we only intend to use this serializer
    as READ-ONLY because we prescribe what Tribes are available in the
    database. We've added a custom validate_name validator because we're
    unable to PUT/POST a demographic objects because this seriliaxer
    attempts to create an object with the name that already exists. I
    think the proper implementation would be to modify the create and
    update methods on this serializer.
    """

    name = serializers.CharField(max_length=200)

    def validate_name(self, value):
        return value

    class Meta:
        model = Tribe
        fields = ('name', 'id')


class DemographicSerializer(serializers.ModelSerializer):
    tribe = TribeSerializer(many=True, partial=True, required=False)

    def validate_tribe(self, value):
        logger.debug(value)
        return value

    class Meta:
        model = Demographic
        fields = ('age', 'gender', 'tribe', 'id')


class KnownLanguageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = KnownLanguage
        fields = (
            'language', 'level_of_proficiency', 'active', 'dialect', 'id')


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(partial=True, required=False)
    demographic = DemographicSerializer(partial=True, required=False)
    known_languages = KnownLanguageSerializer(many=True, required=False, partial=True)
    groups = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=Group.objects.all())

    class Meta:
        model = Person
        fields = ('full_name', 'username', 'uuid', 'user',
                  'demographic', 'known_languages', 'id',
                  'profile_email', 'groups', 'receive_weekly_updates',
                  'leaderboard', 'receive_daily_updates', 'receive_feedback',
                  'receive_emails')
        extra_kwargs = {"username": {"error_messages": {"required": "Give yourself a username"}}}
        validators = []

    def create(self, validated_data):
        if validated_data['groups'] == []:
            del validated_data['groups']

        try:
            user_data = self.initial_data['user']
            user_data = ast.literal_eval(user_data)
            user = User.objects.get(**user_data)
        except Exception as e:
            logger.error(e)
            user = None

        try:
            logger.debug(user)
            logger.debug(validated_data)
            if isinstance(validated_data['known_languages'], list):
                if len(validated_data['known_languages']) == 0:
                    del validated_data['known_languages']
            logger.debug(validated_data)
            person, created = Person.objects.get_or_create(
                user=user, **validated_data)
            logger.debug(person.user)
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        return person

    def validate_username(self, validated_data):
        person = self.instance
        current_user = person.user
        new_username = validated_data
        if new_username:
            if current_user is None:
                # Check if username already exists
                try:
                    user = User.objects.get(username=new_username)
                    raise serializers.ValidationError('Username already exists.')
                except ObjectDoesNotExist:
                    pass

            elif new_username != current_user.username:
                # Check user with uname doesn't already exist
                if User.objects.filter(username=new_username).exists():
                    # Raise validation error 
                    raise serializers.ValidationError('Username already exists.')
                else:
                    # Everything is ka pai
                    pass

        return validated_data

    def validate_profile_email(self, validated_data):
        person = self.instance
        current_user = person.user
        if current_user:
            old_email = person.user.email
        else:
            old_email = None
        new_email = validated_data

        if new_email:
            if new_email != old_email:
                if current_user is None:
                    # Check if the email already exists
                    if EmailAddress.objects.filter(email=new_email).exists():
                        raise serializers.ValidationError(
                            'Email already exists.\
                            Please choose another one or login with your email.')
                else:
                    old_email = EmailAddress.objects.get(user=current_user)
                    if old_email != new_email:
                        if EmailAddress.objects.filter(email=new_email).exists():
                            raise serializers.ValidationError(
                                'Email already exists. Please choose another one\
                                or login with your email.')

        return validated_data
        # return super(PersonSerializer, serlf).validated_data

    def update(self, instance, validated_data):
        person_object = self.instance
        user_object = person_object.user

        attrs = [
            'full_name', 'receive_weekly_updates', 
            'receive_daily_updates', 'receive_feedback', 'leaderboard',
            'receive_emails'
        ]
        for attr in attrs:
            if attr in validated_data.keys():
                setattr(instance, attr, validated_data[attr])
            ## Do we need to set the old values???

        demo, created = Demographic.objects.get_or_create(person=instance)
        if 'demographic' in validated_data.keys():
            demographic = validated_data['demographic']

            try:
                demo.gender = demographic['gender']
            except KeyError:
                demo.gender = None

            try:
                demo.age = demographic['age']
            except KeyError:
                demo.age = None
        else:
            demographic = None

        if 'user' in validated_data.keys():
            new_username = validated_data['username']
            new_email = validated_data['user']['email']
            if instance.user:
                if new_username:
                    instance.user.username = new_username
                if new_email:
                    instance.user.email = new_email
                instance.user.save()
            else:
                user, created = User.objects.get_or_create(
                    username=new_username,
                    email=new_email)
                user.save()
                instance.user = user
        elif 'username' in validated_data.keys():
            instance.username = validated_data['username']
            if instance.user:
                if instance.user.username != instance.username:
                    instance.user.username = instance.username
                    instance.user.save()
            new_email = None
        else:
            new_email = None

        if user_object:
            try:
                email_object, email_created = EmailAddress.objects.get_or_create(
                            user=user_object)
            except MultipleObjectsReturned:
                email_objects = EmailAddress.objects.filter(user=user_object)
                if email_objects.filter(verified=True).count() == 1:
                    email_object = email_objects.get(verified=True)
                else:
                    email_object = email_objects.first()
                    for em in email_objects:
                        if em != email_object:
                            em.delete()
                email_created = False

        if 'profile_email' in validated_data.keys():
            profile_email = validated_data['profile_email']
            if profile_email:
                instance.profile_email = profile_email
                if user_object:
                    instance.user.email = profile_email
                    instance.user.save()
                    if email_object.email != profile_email:
                        email_object.email = profile_email
                        if email_created:
                            email_object.primary = created
                        email_object.verified = False
                        try:
                            email_object.send_confirmation()
                        except:
                            pass
                        email_object.save()
            elif new_email:
                instance.profile_email = new_email
                if instance.user:
                    user = instance.user
                    user_dict = validated_data['user']
                    if instance.user.email == '':
                        instance.user.email = instance.profile_email
                        instance.user.save()
                    if email_object.email != instance.profile_email:
                        email_object.email = instance.profile_email
                        email_object.verified = False
                        try:
                            email_object.send_confirmation()
                        except:
                            pass
                        email_object.save()
            else:
                pass

        if 'username' in validated_data.keys():
            instance.username = validated_data['username']

        if demographic:
            for tribe in demo.tribe.all():
                demo.tribe.remove(tribe)

            for tribe in demographic['tribe']:
                logger.debug(tribe)
                t = Tribe.objects.get(name=tribe['name'])
                demo.tribe.add(t)

        if 'known_languages' in validated_data.keys():
            validated_languages = validated_data['known_languages']
            for vl in validated_languages:
                logger.debug(vl)
                try:
                    kl = KnownLanguage.objects.get(
                        person=instance,
                        language=vl['language']
                    )

                    kl.level_of_proficiency = vl['level_of_proficiency']
                    # kl.accent = vl['accent']
                    kl.dialect = vl['dialect']

                except ObjectDoesNotExist:
                    kl = KnownLanguage.objects.create(
                        person=instance,
                        level_of_proficiency=vl['level_of_proficiency'],
                        dialect=vl['dialect'],
                        # accent=vl['accent'],
                        language=vl['language']
                    )
                kl.save()

        # TODO not sure if this is the correct approach?
        if 'groups' in validated_data.keys():
            instance.groups.set(validated_data['groups'])

        if 'demographic' in validated_data.keys():
            instance.demographic = demo
            instance.demographic.save()
        instance.save()
        
        return instance


class MagicLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    def create(self, validated_data):
        myObject = object()
        myObject.email = validated_data['email']
        return myObject
