"""
Test configuration for pytest-django.
"""
import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner


def pytest_configure(config):
    """
    Configure pytest for Django.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    settings.DEBUG = False
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 0,
        'OPTIONS': {},
        'TIME_ZONE': None,
        'USER': '',
        'HOST': '',
        'PORT': '',
        'PASSWORD': '',
    }
