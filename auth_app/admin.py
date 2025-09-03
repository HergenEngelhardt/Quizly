"""
Admin configuration for auth app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Simple user admin interface.

    Extends the default Django UserAdmin to show basic user information
    with an additional quiz count field.
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
    list_filter = ["is_staff", "is_active", "date_joined"]
    search_fields = ["username", "email"]

    def quiz_count(self, obj):
        """
        Count quizzes for a user.

        Args:
            obj: User object to count quizzes for

        Returns:
            int: Number of quizzes created by the user
        """
        return obj.quizzes.count()

    quiz_count.short_description = "Quizzes"
