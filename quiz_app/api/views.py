"""
Quiz API views for Quizly application.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from quiz_app.models import Quiz
from .serializers import (
    QuizSerializer,
    QuizCreateSerializer,
    QuizUpdateSerializer,
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
            {"detail": "Internal server error."},
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

    def get_user_quiz(self, id, user):
        """
        Get quiz if user owns it.
        """
        try:
            quiz = Quiz.objects.get(id=id)
        except Quiz.DoesNotExist:
            return None, Response(
                {"detail": "Quiz nicht gefunden."}, status=status.HTTP_404_NOT_FOUND
            )

        if quiz.user != user:
            return None, Response(
                {"detail": "Zugriff verweigert - Quiz gehört nicht dem Benutzer."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return quiz, None

    def get(self, request, id):
        """Get specific quiz for authenticated user."""
        quiz, error_response = self.get_user_quiz(id, request.user)
        if error_response:
            return error_response

        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        """Update quiz (full update)."""
        quiz, error_response = self.get_user_quiz(id, request.user)
        if error_response:
            return error_response

        serializer = QuizUpdateSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(QuizSerializer(quiz).data, status=status.HTTP_200_OK)
        return Response({"detail": "Ungültige Anfragedaten."}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        """Partially update quiz."""
        quiz, error_response = self.get_user_quiz(id, request.user)
        if error_response:
            return error_response

        serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(QuizSerializer(quiz).data, status=status.HTTP_200_OK)
        return Response({"detail": "Ungültige Anfragedaten."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """Delete quiz permanently."""
        quiz, error_response = self.get_user_quiz(id, request.user)
        if error_response:
            return error_response

        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
