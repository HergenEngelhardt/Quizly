"""
URL configuration for quiz API.
"""

from django.urls import path
from .quiz_management_views import create_quiz_view, list_quizzes_view
from .quiz_crud_class_views import QuizDetailView
from .quiz_attempt_and_policy_views import (
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
    # User Story 7: Sidebar with today/7-days filter
    path("quizzes/recent/", get_recent_quizzes_view, name="recent_quizzes"),
    # User Story 8 & 9: Quiz playing and evaluation
    path("quizzes/<int:quiz_id>/start/", start_quiz_attempt_view, name="start_quiz"),
    path(
        "attempts/<int:attempt_id>/answer/", save_quiz_answer_view, name="save_answer"
    ),
    path(
        "attempts/<int:attempt_id>/complete/", complete_quiz_view, name="complete_quiz"
    ),
    path(
        "attempts/<int:attempt_id>/results/", get_quiz_results_view, name="quiz_results"
    ),
    # User Story 10: Legal information
    path("privacy-policy/", privacy_policy_view, name="privacy_policy"),
    path("legal-notice/", legal_notice_view, name="legal_notice"),
]
