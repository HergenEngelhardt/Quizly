"""
URL configuration for quiz API.
"""

from django.urls import path
from .views import (
    create_quiz_view,
    list_quizzes_view,
    QuizDetailView,
    get_recent_quizzes_view,
    start_quiz_attempt_view,
    save_quiz_answer_view,
    complete_quiz_view,
    get_quiz_results_view,
    privacy_policy_view,
    legal_notice_view,
)

urlpatterns = [
    path("createQuiz/", create_quiz_view, name="create_quiz"),
    path("quizzes/", list_quizzes_view, name="list_quizzes"),
    path("quizzes/<int:quiz_id>/", QuizDetailView.as_view(), name="quiz_detail"),
    # Additional endpoints for User Stories 7-10
    path("quizzes/recent/", get_recent_quizzes_view, name="recent_quizzes"),
    path("quizzes/<int:quiz_id>/start/", start_quiz_attempt_view, name="start_quiz"),
    path(
        "attempts/<str:attempt_id>/answer/", save_quiz_answer_view, name="save_answer"
    ),
    path(
        "attempts/<str:attempt_id>/complete/", complete_quiz_view, name="complete_quiz"
    ),
    path(
        "attempts/<str:attempt_id>/results/", get_quiz_results_view, name="quiz_results"
    ),
    # Legal pages
    path("privacy/", privacy_policy_view, name="privacy_policy"),
    path("legal/", legal_notice_view, name="legal_notice"),
]
