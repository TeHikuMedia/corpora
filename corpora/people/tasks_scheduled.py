from celery.schedules import crontab

# Will need to add "celery -A proj beat" for these to run.
# this needs to run on the webserver
# celery -A proj beat -s /webapp/logs/celery/celerybeat-schedule

CELERYBEAT_SCHEDULE = {

    'clean_empty_person_models': {
        'task': 'people.tasks.clean_empty_person_models',
        'options': {'task_id': 'clean_empty_person_models'},
        'schedule': crontab(minute='*/25', hour='*'),
        'relative': True,
    },

    'clean_empty_group_models': {
        'task': 'people.tasks.clean_empty_group_models',
        'options': {'task_id': 'clean_empty_group_models'},
        'schedule': crontab(minute='*/20', hour='*'),
        'relative': True,
    },

    'send_person_emails_weekly': {
        'task': 'people.tasks.send_person_emails_weekly',
        'schedule': crontab(minute=0, hour=20, day_of_week='tue'),
    },

    'send_person_emails_daily': {
        'task': 'people.tasks.send_person_emails_daily',

        # only UTC times supported. We could just run our own scheduled - just
        # get beat to run task to schedule task!
        'schedule': crontab(minute=0, hour=21, day_of_week="*"),

    },

    # These aren't necessary as we calculate these on demand - these become redundant.

    # 'calculate_person_scores': {
    #     'task': 'people.tasks.calculate_person_scores',
    #     'schedule': crontab(minute='12,32,52', hour='*', day_of_week='*'),
    # },

    'calculate_group_scores': {
        'task': 'people.tasks.calculate_group_scores',
        'schedule': crontab(minute=47, hour=12, day_of_week='*'),
    },
}
