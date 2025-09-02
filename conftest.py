"""
Test configuration for pytest-django.
"""
import pytest
from django.conf import settings
from django.test.utils import get_runner


def pytest_configure(config):
    """
    Configure pytest for Django.
    """
    settings.DEBUG = False
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
