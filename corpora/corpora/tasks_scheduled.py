from celery.schedules import crontab

# Will need to add "celery -A proj beat" for these to run.
# this needs to run on the webserver
# celery -A proj beat -s /webapp/logs/celery/celerybeat-schedule

CELERYBEAT_SCHEDULE = {
    'erase_tmp_folder': {
        'task': 'corpora.tasks.erase_all_project_files',
        'schedule': crontab(minute=1, hour=1, day_of_week='*'),
    },
}
