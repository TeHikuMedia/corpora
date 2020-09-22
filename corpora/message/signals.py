# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from .models import MessageAction

from django.utils import timezone

from .tasks import send_message


@receiver(models.signals.post_save, sender=MessageAction)
def clear_quality_control_instance_when_object_modified(
        sender, instance, **kwargs):

    if instance.publish:
        if not instance.completed:
            date = instance.publish_date
            send_message.apply_async(
                args=[instance.pk],
                task_id="send-message-{0}".format(
                    instance.pk),
                eta=date
                )
