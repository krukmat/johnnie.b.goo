__author__ = 'matiasleandrokruk'

from settings import *
from celery import app
INSTALLED_APPS = ('django_cassandra_engine',) + INSTALLED_APPS
CELERY_ALWAYS_EAGER = True
app.conf.CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True