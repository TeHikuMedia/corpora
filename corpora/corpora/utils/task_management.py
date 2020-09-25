from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.core.cache import cache


def task_counter(task_id, value):
    key = u"task-{0}-counter".format(task_id)
    task_count = cache.get(key, 0)
    if task_count < 0:
        raise ValueError("Can't have a negative task count.")
    task_count = task_count + value
    cache.set(key, task_count)


def check_task_counter_running(task_id):
    key = u"task-{0}-counter".format(task_id)
    task_count = cache.get(key, None)
    if task_count == 0 or task_count is None:
        return False
    elif taska_count > 0:
        return True
    elif task_count < 0:
        raise ValueError("Can't have a negative task count.")
    else:
        raise NotImplementedError("Some strange stage here.")


def check_and_set_task_running(task_id):
    key = u"task-{0}-isrunning".format(task_id)
    is_running = cache.get(key, False)
    if is_running:
        return True
    else:
        cache.set(key, True)
        return False


def clear_running_tasks(task_id):
    key = u"task-{0}-isrunning".format(task_id)
    cache.delete(key)
