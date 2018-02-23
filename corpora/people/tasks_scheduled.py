from celery.schedules import crontab

# Will need to add "celery -A proj beat" for these to run.
# this needs to run on the webserver
# celery -A proj beat -s /webapp/logs/celery/celerybeat-schedule

CELERYBEAT_SCHEDULE = {
    'clean_empty_person_models': {
        'task': 'people.tasks.clean_empty_person_models',
        'schedule': crontab(minute='42', hour='*', day_of_week='*'),
    },
    'calculate_person_scores': {
        'task': 'people.tasks.calculate_person_scores',
        'schedule': crontab(minute='12,32,52', hour='*', day_of_week='*'),
    },
}