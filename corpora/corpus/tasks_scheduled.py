from celery.schedules import crontab

# Will need to add "celery -A proj beat" for these to run.
# this needs to run on the webserver
# celery -A proj beat -s /webapp/logs/celery/celerybeat-schedule

CELERYBEAT_SCHEDULE = {
    'set_recording_duration': {
        'task': 'corpus.tasks.set_all_recording_durations',
        'schedule': crontab(minute=3, hour=13, day_of_week='*'),
    },
    'transcode_all_audio': {
        'task': 'corpus.tasks.transcode_all_audio',
        'schedule': crontab(minute=30, hour='*/12', day_of_week='*'),
    },
    'set_recording_md5': {
        'task': 'corpus.tasks.set_all_recording_md5',
        'schedule': crontab(minute=42, hour=1, day_of_week=6),
        # 'options': {'task_id': 'set_recordings_md5s'},
    },
}
