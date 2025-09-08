"""
Quiz API views for Quizly application.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from quiz_app.models import Quiz, Question, QuizAttempt
from .serializers import (
    QuizSerializer,
    QuizCreateSerializer,
    QuizUpdateSerializer,
    QuizListSerializer,
    QuizAttemptSerializer,
)
from quiz_app.utils import (
    handle_quiz_creation,
    validate_quiz_creation_data,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_quiz_view(request):
    """Create a new quiz from YouTube URL."""
    try:
        serializer = QuizCreateSerializer(data=request.data)
        url, error = validate_quiz_creation_data(serializer)
        
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
        quiz = handle_quiz_creation(request.user, url)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"detail": f"Error creating quiz: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_quizzes_view(request):
    """
    List all quizzes for the authenticated user.
    """
    try:
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class QuizDetailView(APIView):
    """
    REST API view for quiz detail operations (GET, PUT, PATCH, DELETE).
    """

    permission_classes = [IsAuthenticated]

    def get_user_quiz(self, quiz_id, user):
        """
        Get quiz if user owns it.
        """
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return None, Response(
                {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if quiz.user != user:
            return None, Response(
                {"detail": "Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return quiz, None

    def get(self, request, quiz_id):
        """Get specific quiz for authenticated user."""
        quiz, error_response = self.get_user_quiz(quiz_id, request.user)
        if error_response:
            return error_response

        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, quiz_id):
        """Update quiz (full update)."""
        quiz, error_response = self.get_user_quiz(quiz_id, request.user)
        if error_response:
            return error_response

        serializer = QuizUpdateSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(QuizSerializer(quiz).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, quiz_id):
        """Partially update quiz."""
        quiz, error_response = self.get_user_quiz(quiz_id, request.user)
        if error_response:
            return error_response

        serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(QuizSerializer(quiz).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, quiz_id):
        """Delete quiz permanently."""
        quiz, error_response = self.get_user_quiz(quiz_id, request.user)
        if error_response:
            return error_response

        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recent_quizzes_view(request):
    """Get quizzes created today and last 7 days (User Story 7)."""
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
    """Start a new quiz attempt (User Story 8)."""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
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
    """Save quiz answer (User Story 8 - auto-save progress)."""
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        question_id = request.data.get("question_id")
        answer = request.data.get("answer")

        if not question_id or not answer:
            return Response(
                {"detail": "question_id and answer required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
    """Calculate quiz score percentage."""
    if not attempt.answers:
        return 0.0

    correct_answers = 0
    total_questions = attempt.quiz.questions.count()

    for question in attempt.quiz.questions.all():
        user_answer = attempt.answers.get(str(question.id))
        if user_answer == question.answer:
            correct_answers += 1

    return (correct_answers / total_questions * 100) if total_questions > 0 else 0.0


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_quiz_view(request, attempt_id):
    """Complete quiz and calculate score (User Story 9)."""
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

        if attempt.completed_at:
            return Response(
                {"detail": "Quiz already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        score = calculate_quiz_score(attempt)
        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response(
            {
                "detail": "Quiz completed successfully.",
                "score": score,
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_quiz_results_view(request, attempt_id):
    """Get quiz results with answers comparison (User Story 9)."""
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

        if not attempt.completed_at:
            return Response(
                {"detail": "Quiz not completed yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        questions_with_answers = []
        for question in attempt.quiz.questions.all():
            user_answer = attempt.answers.get(str(question.id))
            questions_with_answers.append(
                {
                    "question": question.question_title,
                    "options": question.question_options,
                    "correct_answer": question.answer,
                    "user_answer": user_answer,
                    "is_correct": user_answer == question.answer,
                }
            )

        return Response(
            {
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "completed_at": attempt.completed_at,
                "questions_with_answers": questions_with_answers,
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


@api_view(["GET"])
@permission_classes([AllowAny])
def privacy_policy_view(request):
    """Privacy policy endpoint (User Story 10)."""
    return Response(
        {
            "title": "Datenschutzerklärung",
            "content": """
        Diese Datenschutzerklärung erklärt, wie Quizly Ihre persönlichen Daten sammelt und verwendet.
        
        1. Datensammlung:
        - Wir sammeln nur notwendige Benutzerdaten (E-Mail, Benutzername)
        - YouTube-URLs werden temporär zur Quiz-Generierung verarbeitet
        - Audio-Dateien werden nur temporär gespeichert und dann gelöscht
        
        2. Datenverwendung:
        - Ihre Daten werden nur zur Bereitstellung des Service verwendet
        - Keine Weitergabe an Dritte
        - Sichere Speicherung in unserer Datenbank
        
        3. Ihre Rechte:
        - Sie können jederzeit Ihre Daten einsehen
        - Sie können Ihr Konto löschen
        - Sie können Änderungen an Ihren Daten vornehmen
        
        Kontakt: [HIER IHRE KONTAKTDATEN EINFÜGEN]
        Stand: September 2025
        """,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def legal_notice_view(request):
    """Legal notice endpoint (User Story 10)."""
    return Response(
        {
            "title": "Impressum",
            "content": """
        Angaben gemäß § 5 TMG:
        
        [HIER IHRE DATEN EINFÜGEN]
        Name: [Ihr Name]
        Adresse: [Ihre Adresse]
        Telefon: [Ihre Telefonnummer]
        E-Mail: [Ihre E-Mail]
        
        Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:
        [Ihr Name]
        [Ihre Adresse]
        
        Haftungsausschluss:
        Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir keine Haftung für die Inhalte externer Links.
        Für den Inhalt der verlinkten Seiten sind ausschließlich deren Betreiber verantwortlich.
        
        Stand: September 2025
        """,
        }
    )
