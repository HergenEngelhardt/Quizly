"""
Quiz API views for Quizly application.
Merged from views.py and views_clean.py to include all functionality.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from quiz_app.models import Quiz
from .serializers import (
    QuizSerializer,
    QuizListSerializer,
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
    Uses QuizListSerializer for optimized list view, with fallback to QuizSerializer.
    """
    try:
        quizzes = Quiz.objects.filter(user=request.user)
        # Primary: Use QuizListSerializer for optimized list display
        try:
            serializer = QuizListSerializer(quizzes, many=True)
        except Exception:
            # Fallback: Use QuizSerializer if QuizListSerializer fails
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
        Returns quiz and error response (if any).
        """
        try:
            quiz = Quiz.objects.get(id=id)
        except Quiz.DoesNotExist:
            return None, Response(
                {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if quiz.user != user:
            return None, Response(
                {"detail": "Access denied - Quiz does not belong to the user."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return quiz, None

    def get(self, request, id):
        """Get specific quiz for authenticated user."""
        try:
            quiz, error_response = self.get_user_quiz(id, request.user)
            if error_response:
                return error_response

            serializer = QuizSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, id):
        """Update quiz (full update)."""
        try:
            quiz, error_response = self.get_user_quiz(id, request.user)
            if error_response:
                return error_response

            serializer = QuizUpdateSerializer(quiz, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(QuizSerializer(quiz).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, id):
        """Partially update quiz."""
        try:
            quiz, error_response = self.get_user_quiz(id, request.user)
            if error_response:
                return error_response

            serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(QuizSerializer(quiz).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, id):
        """Delete quiz permanently."""
        try:
            quiz, error_response = self.get_user_quiz(id, request.user)
            if error_response:
                return error_response

            quiz.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Merged functionality from views.py and views_clean.py
# All features preserved including:
# - QuizListSerializer support with QuizSerializer fallback
# - Comprehensive error handling
# - Detailed error messages for access control
