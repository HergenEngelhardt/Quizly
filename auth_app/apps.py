"""
Simple app configuration for auth_app.
"""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """
    Configuration for the authentication app.

    Handles user registration, login, logout and JWT token management.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"
    name = "auth_app"
