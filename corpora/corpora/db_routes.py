import random
from django.conf import settings

class ReadRouter:

    def db_for_read(self, model, **hints):
        '''
        A simple router to go between primary and read replica databases
        '''
        return random.choice(list(settings.DATABASES.keys()))

    def allow_relation(obj1, obj2, **hints):
        '''
        Always allow relations. This is needed for read only
        select related.
        '''
        return True
