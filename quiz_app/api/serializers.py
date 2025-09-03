"""
Serializers for quiz API endpoints.
"""

from rest_framework import serializers
from quiz_app.models import Quiz, Question, QuizAttempt
from django.core.validators import URLValidator
from urllib.parse import urlparse


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model.
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
    Serializer for Quiz model with questions.
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "video_url",
            "created_at",
            "updated_at",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuizCreateSerializer(serializers.Serializer):
    """
    Serializer for creating quiz from YouTube URL.
    """

    url = serializers.URLField(validators=[URLValidator()])

    def validate_url(self, value):
        """
        Validate that URL is a YouTube URL.
        """
        parsed_url = urlparse(value)
        valid_domains = ["youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"]

        if parsed_url.netloc not in valid_domains:
            raise serializers.ValidationError("URL must be a valid YouTube URL.")

        return value


class QuizUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating quiz (title and description only).
    """

    class Meta:
        model = Quiz
        fields = ["title", "description", "video_url"]

    def validate_video_url(self, value):
        """
        Validate that URL is a YouTube URL.
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


class QuizListSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz list view (without questions content).
    """

    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "video_url",
            "created_at",
            "updated_at",
            "questions_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_questions_count(self, obj):
        """
        Get count of questions for this quiz.
        """
        return obj.questions.count()


class QuizAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz attempts.
    """

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "answers",
            "score",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "quiz",
            "score",
            "completed_at",
            "created_at",
            "updated_at",
        ]
