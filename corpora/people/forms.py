# -*- coding: utf-8 -*-
from django import forms
from people.models import KnownLanguage, Person, Demographic
from people.helpers import get_or_create_person
from corpus.base_settings import LANGUAGES, LANGUAGE_CODE, DIALECTS, ACCENTS
from dal import autocomplete
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.translation import ugettext as _
from django.db.models import Q

# from django.conf.settings import LANGUAGES

# form = modelform_factory(KnownLanguage, fields = ('language', 'level_or_proficiency'), initial = 'set person somehow, max_num = len(available_languages)')

import logging
logger = logging.getLogger('corpora')


class KnownLanguageFormWithPerson(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        person = kwargs.pop('person', None)
        require_proficiency = kwargs.pop('require_proficiency', None)

        super(KnownLanguageFormWithPerson, self).__init__(*args, **kwargs)

        instance = kwargs['instance']  # this is a known language instance.

        # I have a feeling this will braeak when there's an empty instance - e.g. known language is None
        # We'll need to use autocomplete light to update fields when someone adds a new language.

        language_accents = []
        for i in range(len(ACCENTS)):
            if ACCENTS[i][0] == instance.language:
                language_accents = ACCENTS[i][1]

        language_dialects = []
        for i in range(len(DIALECTS)):
            if DIALECTS[i][0] == instance.language:
                language_dialects = DIALECTS[i][1]

        # if language_accents:
        #     self.fields['accent'].choices = ()
        #     self.fields['accent'].choices.append(BLANK_CHOICE_DASH)
        #     for i in language_accents:
        #         self.fields['accent'].choices.append(i)
        # if language_dialects:
        #     self.fields['dialect'].choices = ()
        #     self.fields['dialect'].choices.append(BLANK_CHOICE_DASH)
        #     for i in language_dialects:
        #         self.fields['dialect'].choices.append(i)

        self.fields['language'].disabled = True

        if language_accents:
            self.fields['accent'].choices = BLANK_CHOICE_DASH + list(language_accents)
        if language_dialects:
            self.fields['dialect'].choices = BLANK_CHOICE_DASH + list(language_dialects)

        # temporarily disabling accents
        del self.fields['accent']

        if require_proficiency:
            self.fields['level_of_proficiency'].required = require_proficiency


class PersonForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Person
        fields = (
            'full_name',
            'email',
            'username',
            'receive_weekly_updates',
            'receive_daily_updates',
            'receive_feedback',
            'receive_emails',
            'leaderboard')


class GroupsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(GroupsForm, self).__init__(*args, **kwargs)

        if not request.user.is_authenticated:
            self.fields['groups'].help_text = \
                "If you can't find your group, log in or sign up to create " \
                "a new one."

    class Meta:
        model = Person
        fields = ('groups', )
        widgets = {
            'groups': autocomplete.Select2Multiple(
                url='people:groups-autocomplete',
                attrs={
                    # 'data-placeholder': '',
                    # 'data-minimum-input-length': 3,
                },)
        }


class DemographicForm(forms.ModelForm):
    # date_of_birth = DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Demographic
        fields = ('age', 'gender', 'tribe')
        widgets = {
            'tribe': autocomplete.ModelSelect2Multiple(url='people:tribe-autocomplete')
        }


class DemographicFormAdmin(forms.ModelForm):
    # date_of_birth = DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Demographic
        fields = ('__all__')
        widgets = {
            'tribe': autocomplete.ModelSelect2Multiple(url='people:tribe-autocomplete')
        }


class SendEmailForm(forms.Form):
    daily = forms.BooleanField(required=False)
    weekly = forms.BooleanField(required=False)


class ResendEmailVerificationForm(forms.Form):
    resend = forms.BooleanField(required=True)
    # redirect = forms.CharField(max_length=128)

class UnsubscribeForm(forms.Form):
    email = forms.EmailField(required=True)

    def unsubscribe(self):
        email = self.cleaned_data['email']
        person = Person.objects.filter(
            Q(profile_email=email) | Q(user__email=email) )
        if person.exists():
            for p in person:
                p.receive_emails = False
                p.receive_feedback = False
                p.receive_daily_updates = False
                p.receive_weekly_updates = False
                p.save()
            return True
        else:
            return False
