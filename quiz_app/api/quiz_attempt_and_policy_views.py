"""
Additional API views for User Stories 7-10.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from quiz_app.models import Quiz, QuizAttempt
from .serializers import QuizListSerializer, QuizAttemptSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recent_quizzes_view(request):
    """
    Get quizzes created today and last 7 days (User Story 7).
    """
    try:
        today = timezone.now().date()
        last_week = today - timedelta(days=7)

        today_quizzes = Quiz.objects.filter(user=request.user, created_at__date=today)

        week_quizzes = Quiz.objects.filter(
            user=request.user,
            created_at__date__gte=last_week,
            created_at__date__lt=today,
        )

        data = {
            "today": QuizListSerializer(today_quizzes, many=True).data,
            "last_7_days": QuizListSerializer(week_quizzes, many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_quiz_attempt_view(request, quiz_id):
    """
    Start a new quiz attempt (User Story 8).
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)

        # Create new attempt
        attempt = QuizAttempt.objects.create(quiz=quiz, user=request.user, answers={})

        serializer = QuizAttemptSerializer(attempt)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Quiz.DoesNotExist:
        return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def save_quiz_answer_view(request, attempt_id):
    """
    Save quiz answer (User Story 8 - auto-save progress).
    """
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

        question_id = request.data.get("question_id")
        answer = request.data.get("answer")

        if not question_id or not answer:
            return Response(
                {"detail": "question_id and answer required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update answers
        attempt.answers[str(question_id)] = answer
        attempt.save()

        return Response(
            {"detail": "Answer saved successfully."}, status=status.HTTP_200_OK
        )

    except QuizAttempt.DoesNotExist:
        return Response(
            {"detail": "Quiz attempt not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def calculate_quiz_score(attempt):
    """
    Calculate quiz score based on user answers.
    """
    questions = attempt.quiz.questions.all()
    correct_answers = 0
    total_questions = questions.count()

    for question in questions:
        user_answer = attempt.answers.get(str(question.id))
        if user_answer == question.answer:
            correct_answers += 1

    score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    return score, correct_answers, total_questions


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_quiz_view(request, attempt_id):
    """
    Complete quiz and calculate score (User Story 9).
    """
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

        if attempt.completed_at:
            return Response(
                {"detail": "Quiz already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        score, correct_answers, total_questions = calculate_quiz_score(attempt)

        # Update attempt
        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response(
            {
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "percentage": f"{score:.1f}%",
            },
            status=status.HTTP_200_OK,
        )

    except QuizAttempt.DoesNotExist:
        return Response(
            {"detail": "Quiz attempt not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def create_question_result(question, user_answer):
    """
    Create result data for a single question.
    """
    is_correct = user_answer == question.answer

    return {
        "question": question.question_title,
        "options": question.question_options,
        "correct_answer": question.answer,
        "user_answer": user_answer,
        "is_correct": is_correct,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_quiz_results_view(request, attempt_id):
    """
    Get detailed quiz results with answers (User Story 9).
    """
    try:
        attempt = get_object_or_404(
            QuizAttempt, id=attempt_id, user=request.user, completed_at__isnull=False
        )

        questions = attempt.quiz.questions.all()
        results = []

        for question in questions:
            user_answer = attempt.answers.get(str(question.id))
            results.append(create_question_result(question, user_answer))

        return Response(
            {
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "completed_at": attempt.completed_at,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

    except QuizAttempt.DoesNotExist:
        return Response(
            {"detail": "Quiz attempt not found or not completed."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def privacy_policy_view(request):
    """
    Privacy policy endpoint (User Story 10).
    """
    privacy_content = {
        "title": "Datenschutzerklärung - Quizly",
        "last_updated": "2025-01-01",
        "content": [
            {
                "section": "1. Datenerhebung",
                "text": "Wir erheben nur die notwendigen Daten für die Bereitstellung unserer Quiz-Services.",
            },
            {
                "section": "2. Verwendung der Daten",
                "text": "Ihre Daten werden ausschließlich zur Bereitstellung der Quizly-Services verwendet.",
            },
            {
                "section": "3. Datenspeicherung",
                "text": "Alle Daten werden sicher in unserer Datenbank gespeichert und verschlüsselt übertragen.",
            },
            {
                "section": "4. Ihre Rechte",
                "text": "Sie haben das Recht auf Auskunft, Berichtigung und Löschung Ihrer personenbezogenen Daten.",
            },
        ],
    }

    return Response(privacy_content, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def legal_notice_view(request):
    """
    Legal notice/Impressum endpoint (User Story 10).
    """
    legal_content = {
        "title": "Impressum - Quizly",
        "operator": {
            "name": "[Betreibername einfügen]",
            "address": "[Adresse einfügen]",
            "email": "[Email einfügen]",
            "phone": "[Telefon einfügen]",
        },
        "disclaimer": "Die Inhalte unserer Seiten wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen.",
        "last_updated": "2025-01-01",
    }

    return Response(legal_content, status=status.HTTP_200_OK)
