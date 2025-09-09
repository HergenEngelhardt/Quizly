"""
URL configuration for quiz API.
"""

from django.urls import path
from .views import (
    create_quiz_view,
    list_quizzes_view,
    QuizDetailView,
)

urlpatterns = [
    path("createQuiz/", create_quiz_view, name="create_quiz"),
    path("quizzes/", list_quizzes_view, name="list_quizzes"),
    path("quizzes/<int:id>/", QuizDetailView.as_view(), name="quiz_detail"),
]
