"""
Simple models for the quiz application.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator


class Quiz(models.Model):
    """
    Quiz model for YouTube video-based quizzes.

    Represents a quiz created from a YouTube video with questions.
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(validators=[URLValidator()])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quizzes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """
        String representation of quiz.

        Returns:
            str: Quiz title and username
        """
        return f"{self.title or 'Untitled Quiz'} - {self.user.username}"


class Question(models.Model):
    """
    Question model for quiz questions.

    Represents individual questions within a quiz with multiple choice options.
    """

    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_title = models.TextField()
    question_options = models.JSONField(default=list)
    answer = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        """
        String representation of question.

        Returns:
            str: Question identifier with quiz title
        """
        return f"Question for {self.quiz.title or 'Untitled Quiz'}"


class QuizAttempt(models.Model):
    """
    Quiz attempt model for tracking user quiz sessions.

    Stores user answers and scores for completed quizzes.
    """

    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    answers = models.JSONField(default=dict)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """
        String representation of quiz attempt.

        Returns:
            str: Username and quiz title
        """
        return f"{self.user.username} - {self.quiz.title or 'Untitled Quiz'}"


class BlacklistedToken(models.Model):
    """
    Model for storing blacklisted JWT tokens.

    Keeps track of invalid tokens for security purposes.
    """

    token = models.TextField(unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["token"])]

    def __str__(self):
        """
        String representation of blacklisted token.

        Returns:
            str: Blacklist timestamp
        """
        return f"Blacklisted token - {self.blacklisted_at}"
