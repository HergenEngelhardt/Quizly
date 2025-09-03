"""
Admin configuration for auth app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Customize the default User admin
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User admin with additional information.
    """

    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
        "quiz_count",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    def quiz_count(self, obj):
        """
        Display number of quizzes created by user.
        """
        return obj.quizzes.count()

    quiz_count.short_description = "Quizzes"
