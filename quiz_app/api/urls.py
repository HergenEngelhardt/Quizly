"""
URL configuration for quiz API.
"""
from django.urls import path
from .views import (
    create_quiz_view,
    list_quizzes_view,
    get_quiz_view,
    update_quiz_view,
    partial_update_quiz_view,
    delete_quiz_view
)

urlpatterns = [
    path('createQuiz/', create_quiz_view, name='create_quiz'),
    path('quizzes/', list_quizzes_view, name='list_quizzes'),
    path('quizzes/<uuid:quiz_id>/', get_quiz_view, name='get_quiz'),
    path('quizzes/<uuid:quiz_id>/', update_quiz_view, name='update_quiz'),
    path('quizzes/<uuid:quiz_id>/', partial_update_quiz_view, name='partial_update_quiz'),
    path('quizzes/<uuid:quiz_id>/', delete_quiz_view, name='delete_quiz'),
]
