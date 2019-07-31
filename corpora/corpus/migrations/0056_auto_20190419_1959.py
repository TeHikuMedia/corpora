# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-19 07:59
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist

from django.db import migrations, IntegrityError, transaction
import sys


def convert_quality_controls(apps, schema_editor):
    from django.contrib.contenttypes.models import ContentType
    db_alias = schema_editor.connection.alias

    RecordingQualityControl = \
        apps.get_model('corpus', 'RecordingQualityControl')
    SentenceQualityControl = \
        apps.get_model('corpus', 'SentenceQualityControl')

    Recording = \
        apps.get_model('corpus', 'Recording')
    Sentence = \
        apps.get_model('corpus', 'Sentence')

    quality_controls = RecordingQualityControl.objects.using(db_alias).all()

    num_qc = quality_controls.count()
    num_rqc = quality_controls.filter(content_type__model='recording').count()
    num_sqc = quality_controls.filter(content_type__model='sentence').count()

    if num_qc != num_sqc + num_rqc:
        raise Exception("{0} != {1} + {2}".format(num_qc, num_sqc, num_rqc))

    to_delete = []
    errors = []
    r_count = 0
    s_count = 0
    print('\n')
    for qc in quality_controls:

        ct = ContentType.objects.get(
            model=qc.content_type.model,
            app_label=qc.content_type.app_label)
        try:
            content_object = ct.get_object_for_this_type(pk=qc.object_id)
        except ObjectDoesNotExist:
            errors.append({
                'error_type': 'ObjectDoesNotExist',
                'object_description': '{0}.{1}'.format(
                    qc.content_type.app_label, qc.content_type.model),
                'note': 'Could not get content object.',
                })
            content_object = None

        if 'sentence' in qc.content_type.model:
            s_count = s_count + 1
            sys.stdout.write('\rProcessing: {0: 6d} / {1: 6d} {2: 6d} / {3: 6d}'.format(
                s_count, num_sqc, r_count, num_rqc))
            sys.stdout.flush()
            try:
                sentence = Sentence.objects.get(pk=qc.object_id)

                sqc = SentenceQualityControl.objects.using(db_alias).create(
                    good=qc.good,
                    bad=qc.bad,
                    approved=qc.approved,
                    approved_by=qc.approved_by,
                    trash=qc.trash,
                    updated=qc.updated,
                    person=qc.person,
                    notes=qc.notes,
                    machine=qc.machine,
                    source=qc.source,
                    sentence=sentence)

            except ObjectDoesNotExist:
                errors.append({
                    'error_type': 'ObjectDoesNotExist',
                    'object_description': 'Sentence: {0}'.format(qc.object_id),
                    'note': 'Could not get sentence.'
                    })

                sqc = None

            if not sqc:
                errors.append({
                    'error_type': 'MigrationError',
                    'object_description': 'Sentence: {0}'.format(qc.object_id),
                    })
            else:
                sqc.save()
                to_delete.append(qc.pk)

        elif 'recording' in qc.content_type.model:
            r_count = r_count + 1
            sys.stdout.write('\rProcessing: {0: 6d} / {1: 6d} {2: 6d} / {3: 6d}'.format(
                s_count, num_sqc, r_count, num_rqc))
            sys.stdout.flush()

            try:
                recording = Recording.objects.using(db_alias).get(
                    pk=qc.object_id)
                qc.recording = recording
                qc.save()
            except ObjectDoesNotExist:
                errors.append({
                    'error_type': 'MigrationError',
                    'object_description': 'Recording: {0}'.format(qc.object_id),
                    })

        else:
            errors.append({
                'error_type': 'UnknownError',
                'object_description': '{0}.{1}'.format(
                    qc.content_type.app_label, qc.content_type.model),
                })

    print('\nProcessed:  {0: 6d} / {1: 6d} {2: 6d} / {3: 6d}'.format(
                s_count, num_sqc, r_count, num_rqc))

    d_count = 0
    for pk in to_delete:

        try:
            qc = RecordingQualityControl.objects.using(db_alias).get(pk=pk)
            qc.delete()
            d_count = d_count + 1

            sys.stdout.write('\rDeleting:   {0: 6d} / {1: 6d}'.format(
                    d_count, len(to_delete)))
            sys.stdout.flush()

        except ObjectDoesNotExist:
            errors.append({
                'error_type': 'DeletionError',
                'object_description': 'Recording: {0}'.format(pk),
                })

    print('\nDeleted:    {0: 6d} / {1: 6d}\r'.format(
            d_count, len(to_delete)))

    for error in errors:
        print(error)

    if num_rqc != RecordingQualityControl.objects.using(db_alias).all().count():
        raise Exception('Error migrations recordings qcs')
    if num_sqc != SentenceQualityControl.objects.using(db_alias).all().count():
        raise Exception('Error migrations sentence qcs')


def restore_quality_controls(apps, schema_editor):

    ContentType = apps.get_model('contenttypes', 'ContentType')
    db_alias = schema_editor.connection.alias

    RecordingQualityControl = \
        apps.get_model('corpus', 'RecordingQualityControl')
    SentenceQualityControl = \
        apps.get_model('corpus', 'SentenceQualityControl')

    Recording = \
        apps.get_model('corpus', 'Recording')
    Sentence = \
        apps.get_model('corpus', 'Sentence')

    recording_quality_controls = RecordingQualityControl.objects.using(db_alias).all()
    sentence_quality_controls = SentenceQualityControl.objects.using(db_alias).all()

    ct = ContentType.objects.get(
        model='recording',
        app_label='corpus')

    to_delete = []
    for qc in recording_quality_controls:
        qc.object_id = qc.recording.pk
        qc.content_type = ct
        qc.save()

    ct = ContentType.objects.get(
        model='sentence',
        app_label='corpus')

    for qc in sentence_quality_controls:
        rqc = RecordingQualityControl.objects.using(db_alias).create(
            good=qc.good,
            bad=qc.bad,
            approved=qc.approved,
            approved_by=qc.approved_by,
            trash=qc.trash,
            updated=qc.updated,
            person=qc.person,
            notes=qc.notes,
            machine=qc.machine,
            content_type=ct,
            object_id=qc.sentence.pk,
            source=qc.source)

        if not rqc:
            print("Did not create recording qc")
        else:
            rqc.save()
            to_delete.append(qc.pk)

    for pk in to_delete:
        qc = SentenceQualityControl.objects.using(db_alias).get(pk=pk)
        qc.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0055_auto_20190420_1549'),
    ]

    operations = [
        migrations.RunPython(
            convert_quality_controls,
            restore_quality_controls),
    ]