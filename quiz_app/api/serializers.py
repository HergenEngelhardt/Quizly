"""
Simple serializers for quiz API endpoints.
"""

from rest_framework import serializers
from quiz_app.models import Quiz, Question
from django.core.validators import URLValidator
from urllib.parse import urlparse


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz questions with full details.

    Handles question data for API responses including timestamps.
    """

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuestionListSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz questions in list view.

    Handles question data for API responses without timestamps.
    """

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
        ]
        read_only_fields = ["id"]


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for complete quiz data with questions.

    Used for API responses that include full quiz information with timestamps.
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuizListSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz list view.

    Used for API responses in list view with questions without timestamps.
    """

    questions = QuestionListSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuizCreateSerializer(serializers.Serializer):
    """
    Serializer for creating quiz from YouTube URL.

    Validates that the provided URL is a valid YouTube URL.
    """

    url = serializers.URLField(validators=[URLValidator()])

    def validate_url(self, value):
        """
        Validate YouTube URL format.

        Args:
            value (str): URL to validate

        Returns:
            str: Validated URL

        Raises:
            ValidationError: If URL is not a YouTube URL
        """
        parsed_url = urlparse(value)
        valid_domains = ["youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"]

        if parsed_url.netloc not in valid_domains:
            raise serializers.ValidationError("URL must be a valid YouTube URL.")

        return value


class QuizUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating quiz information.

    Allows updating title, description, and video URL.
    """

    class Meta:
        model = Quiz
        fields = ["title", "description", "video_url"]

    def validate_video_url(self, value):
        """
        Validate YouTube URL format for updates.

        Args:
            value (str): URL to validate

        Returns:
            str: Validated URL

        Raises:
            ValidationError: If URL is not a YouTube URL
        """
        if value:
            parsed_url = urlparse(value)
            valid_domains = [
                "youtube.com",
                "www.youtube.com",
                "youtu.be",
                "m.youtube.com",
            ]

            if parsed_url.netloc not in valid_domains:
                raise serializers.ValidationError("URL must be a valid YouTube URL.")

        return value
