"""
URL configuration for authentication API.
"""
from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    refresh_token_view
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', refresh_token_view, name='token_refresh'),
]
