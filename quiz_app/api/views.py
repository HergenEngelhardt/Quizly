"""
Quiz API views for Quizly application.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from quiz_app.models import Quiz, Question
from .serializers import (
    QuizSerializer, QuizCreateSerializer, QuizUpdateSerializer,
    QuizListSerializer, QuestionSerializer
)
from quiz_app.utils import (
    download_youtube_audio, transcribe_audio, 
    generate_quiz_from_transcript, cleanup_temp_file,
    get_video_info, extract_youtube_id
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz_view(request):
    """
    Create a new quiz from YouTube URL.
    """
    try:
        serializer = QuizCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        url = serializer.validated_data['url']
        user = request.user
        
        # Get video info
        video_info = get_video_info(url)
        
        # Download audio
        audio_file = download_youtube_audio(url)
        
        try:
            # Transcribe audio
            transcript = transcribe_audio(audio_file)
            
            # Generate quiz
            quiz_data = generate_quiz_from_transcript(
                transcript, 
                video_info.get('title', '')
            )
            
            # Create quiz
            quiz = Quiz.objects.create(
                title=quiz_data.get('title', video_info.get('title', 'Untitled Quiz')),
                description=quiz_data.get('description', ''),
                video_url=url,
                user=user
            )
            
            # Create questions
            for question_data in quiz_data['questions']:
                Question.objects.create(
                    quiz=quiz,
                    question_title=question_data['question_title'],
                    question_options=question_data['question_options'],
                    answer=question_data['answer']
                )
            
            # Serialize response
            response_serializer = QuizSerializer(quiz)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        finally:
            # Clean up temporary audio file
            cleanup_temp_file(audio_file)
            
    except Exception as e:
        return Response(
            {"detail": f"Error creating quiz: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_quizzes_view(request):
    """
    List all quizzes for authenticated user.
    """
    try:
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizSerializer(quizzes, many=True)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_view(request, quiz_id):
    """
    Get specific quiz for authenticated user.
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
        serializer = QuizSerializer(quiz)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
    except Quiz.DoesNotExist:
        return Response(
            {"detail": "Quiz not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_quiz_view(request, quiz_id):
    """
    Update quiz (full update).
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
        
        serializer = QuizUpdateSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_serializer = QuizSerializer(quiz)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Quiz.DoesNotExist:
        return Response(
            {"detail": "Quiz not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partial_update_quiz_view(request, quiz_id):
    """
    Partially update quiz.
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
        
        serializer = QuizUpdateSerializer(
            quiz, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            response_serializer = QuizSerializer(quiz)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Quiz.DoesNotExist:
        return Response(
            {"detail": "Quiz not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_quiz_view(request, quiz_id):
    """
    Delete quiz permanently.
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
        quiz.delete()
        
        return Response(
            None,
            status=status.HTTP_204_NO_CONTENT
        )
        
    except Quiz.DoesNotExist:
        return Response(
            {"detail": "Quiz not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
