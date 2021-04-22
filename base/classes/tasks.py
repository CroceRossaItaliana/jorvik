from celery import Task
from django.db import transaction


class TransactionAwareTask(Task):
    abstract = True

    def apply_async(self, *args, **kwargs):
        transaction.on_commit(
            lambda: super(TransactionAwareTask, self).apply_async(
                *args, **kwargs))
