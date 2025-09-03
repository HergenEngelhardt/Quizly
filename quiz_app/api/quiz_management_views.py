"""
Quiz API views for Quizly application.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from quiz_app.models import Quiz, Question
from .serializers import (
    QuizSerializer,
    QuizCreateSerializer,
    QuizUpdateSerializer,
)
from quiz_app.utils import (
    download_youtube_audio,
    transcribe_audio,
    generate_quiz_from_transcript,
    cleanup_temp_file,
    get_video_info,
)


def validate_quiz_creation_data(request):
    """
    Validate request data for quiz creation.
    """
    serializer = QuizCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return serializer.validated_data["url"], None


def process_video_transcription(url):
    """
    Process video URL to transcript.
    """
    video_info = get_video_info(url)
    audio_file = download_youtube_audio(url)

    try:
        transcript = transcribe_audio(audio_file)
        return transcript, audio_file, video_info
    except Exception:
        cleanup_temp_file(audio_file)
        raise


def create_quiz_from_data(user, url, quiz_data, video_info):
    """
    Create quiz object from processed data.
    """
    quiz = Quiz.objects.create(
        title=quiz_data.get("title", video_info.get("title", "Untitled Quiz")),
        description=quiz_data.get("description", ""),
        video_url=url,
        user=user,
    )

    for question_data in quiz_data["questions"]:
        Question.objects.create(
            quiz=quiz,
            question_title=question_data["question_title"],
            question_options=question_data["question_options"],
            answer=question_data["answer"],
        )

    return quiz


def cleanup_quiz_creation(audio_file_path):
    """
    Cleanup temporary files after quiz creation.
    """
    cleanup_temp_file(audio_file_path)


def handle_quiz_creation(user, url):
    """
    Handle the complete quiz creation process.
    """
    transcript, audio_file, video_info = process_video_transcription(url)
    try:
        quiz_data = generate_quiz_from_transcript(
            transcript, video_info.get("title", "")
        )
        return create_quiz_from_data(user, url, quiz_data, video_info)
    finally:
        cleanup_quiz_creation(audio_file)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_quiz_view(request):
    """
    Create a new quiz from YouTube URL.
    """
    try:
        url, error_response = validate_quiz_creation_data(request)
        if error_response:
            return error_response

        quiz = handle_quiz_creation(request.user, url)
        response_serializer = QuizSerializer(quiz)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"detail": f"Error creating quiz: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_quizzes_view(request):
    """
    List all quizzes for authenticated user.
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


def validate_quiz_access(quiz_id, user):
    """
    Validate quiz access and return quiz or error response.
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
    except Quiz.DoesNotExist:
        return None, Response(
            {"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if quiz.user != user:
        return None, Response(
            {"detail": "Access denied - Quiz does not belong to user."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return quiz, None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_quiz_view(request, quiz_id):
    """
    Get specific quiz for authenticated user.
    """
    try:
        quiz, error_response = validate_quiz_access(quiz_id, request.user)
        if error_response:
            return error_response

        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def handle_quiz_update(quiz, request_data, partial=False):
    """
    Handle quiz update logic.
    """
    serializer = QuizUpdateSerializer(quiz, data=request_data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        response_serializer = QuizSerializer(quiz)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_quiz_view(request, quiz_id):
    """
    Update quiz (full update).
    """
    try:
        quiz, error_response = validate_quiz_access(quiz_id, request.user)
        if error_response:
            return error_response

        return handle_quiz_update(quiz, request.data, partial=False)

    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def partial_update_quiz_view(request, quiz_id):
    """
    Partially update quiz.
    """
    try:
        quiz, error_response = validate_quiz_access(quiz_id, request.user)
        if error_response:
            return error_response

        return handle_quiz_update(quiz, request.data, partial=True)

    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_quiz_view(request, quiz_id):
    """
    Delete quiz permanently.
    """
    try:
        quiz, error_response = validate_quiz_access(quiz_id, request.user)
        if error_response:
            return error_response

        quiz.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
