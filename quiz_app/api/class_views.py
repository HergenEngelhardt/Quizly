"""
Class-based views for Quiz API.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from quiz_app.models import Quiz
from .serializers import QuizSerializer, QuizUpdateSerializer


class QuizDetailView(APIView):
    """
    REST API view for quiz detail operations (GET, PUT, PATCH, DELETE).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        """Get specific quiz for authenticated user."""
        try:
            try:
                quiz = get_object_or_404(Quiz, id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
                )
            
            if quiz.user != request.user:
                return Response(
                    {"detail": "Access denied - Quiz does not belong to user."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = QuizSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, quiz_id):
        """Update quiz (full update)."""
        try:
            try:
                quiz = get_object_or_404(Quiz, id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
                )
            
            if quiz.user != request.user:
                return Response(
                    {"detail": "Access denied - Quiz does not belong to user."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = QuizUpdateSerializer(quiz, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_serializer = QuizSerializer(quiz)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, quiz_id):
        """Partially update quiz."""
        try:
            try:
                quiz = get_object_or_404(Quiz, id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
                )
            
            if quiz.user != request.user:
                return Response(
                    {"detail": "Access denied - Quiz does not belong to user."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_serializer = QuizSerializer(quiz)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, quiz_id):
        """Delete quiz permanently."""
        try:
            try:
                quiz = get_object_or_404(Quiz, id=quiz_id)
            except Quiz.DoesNotExist:
                return Response(
                    {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
                )
            
            if quiz.user != request.user:
                return Response(
                    {"detail": "Access denied - Quiz does not belong to user."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            quiz.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
            )
