from celery.schedules import crontab

# Will need to add "celery -A proj beat" for these to run.
# this needs to run on the webserver
# celery -A proj beat -s /webapp/logs/celery/celerybeat-schedule

CELERYBEAT_SCHEDULE = {
    # 'asg_launch_watchdog': {
    #     'task': 'transcription.tasks.launch_watcher',
    #     'schedule': crontab(minute='*/5'),
    # },
    # 'transcribe_all_recordings': {
    #     'task': 'transcription.tasks.transcribe_all_recordings',
    #     'schedule': crontab(minute='*/30', hour='1,3', day_of_week='*'),
    #     # 'options': {'task_id': 'xribe_rec_without_rev'},
    # },
    # 'transcribe_recordings_without_reviews': {
    #     'task': 'transcription.tasks.transcribe_recordings_without_reviews',
    #     'schedule': crontab(minute='*/30', hour='1,3', day_of_week='*'),
    #     # 'options': {'task_id': 'xribe_rec_without_rev'},
    # },
    'calc_wer_when_null': {
        'task': 'transcription.tasks.calculate_wer_for_null',
        'schedule': crontab(minute=42, hour=2, day_of_week='*'),
        # 'options': {'task_id': 'xribe_rec_without_rev'},
    },
    'calc_wer_when_null': {
        'task': 'transcription.tasks.calculate_wer_for_null',
        'schedule': crontab(minute='*/10', hour=2, day_of_week='*'),
        # 'options': {'task_id': 'xribe_rec_without_rev'},
    },
    'check_for_and_transcribe_blank_segments': {
        'task': 'transcription.tasks.check_and_transcribe_blank_segments',
        'schedule': crontab(minute='*/5', hour='*', day_of_week='*'),
    },
    'check_for_and_transcribe_blank_audiofiletranscriptions': {
        'task': 'transcription.tasks.check_and_transcribe_blank_audiofiletranscriptions',
        'schedule': crontab(minute=42, hour=1, day_of_week='*'),
    }
    # 'delete_transcriptions_for_approved_recordings': {
    #     'task': 'transcription.tasks.delete_transcriptions_for_approved_recordings',
    #     'schedule': crontab(minute=42, hour='*/2', day_of_week='*'),
    #     # 'options': {'task_id': 'del_xtions_for_approved_recs'},
    # },
}
