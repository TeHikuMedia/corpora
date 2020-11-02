import random
from django.conf import settings

class ReadRouter:

    def db_for_read(self, model, **hints):
        '''
        A simple router to go between primary and read replica databases
        '''
        return random.choice(list(settings.DATABASES.keys()))

    def db_for_write(self, model, **hints):
        '''
        Only use default for writing
        '''
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        '''
        Always allow relations. This is needed for read only
        select related.
        '''
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'
