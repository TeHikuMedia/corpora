# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.utils import timezone
from allauth.account import signals

from .models import Person, Group
from .helpers import get_or_create_person

from people.tasks import update_group_score


@receiver(signals.user_signed_up)
def user_signed_ip(request, user, **kwargs):
    request.user = user
    person = get_or_create_person(request)
    person.just_signed_up = True
    person.save()


# @receiver(models.signals.pre_save, sender=Person)
# def update_group_score_when_person_changes_group(
#         sender, instance, **kwargs):

#     try:
#         old_instance = Person.objects.get(pk=instance.pk)

#         old_groups = old_instance.groups.all()

#         if len(old_groups) > 0:
#             for g in old_groups:
#                 update_group_score.apply_async(
#                     args=[g.pk],
#                     task_id="update-group-score-{0}-{1}".format(
#                         g.pk, timezone.now().strftime("%H")),
#                     countdown=60*10)

#     except ObjectDoesNotExist:
#         pass
