"""
Quiz app models for Quizly application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
import uuid


class Quiz(models.Model):
    """
    Quiz model representing a quiz created from YouTube video.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(validators=[URLValidator()])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return f"{self.title or 'Untitled Quiz'} - {self.user.username}"


class Question(models.Model):
    """
    Question model representing individual quiz questions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_title = models.TextField()
    question_options = models.JSONField(default=list)  # Array of 4 options
    answer = models.CharField(max_length=500)  # Correct answer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    
    def __str__(self):
        return f"Question for {self.quiz.title or 'Untitled Quiz'}"


class QuizAttempt(models.Model):
    """
    Quiz attempt model for tracking user quiz sessions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    answers = models.JSONField(default=dict)  # question_id: selected_answer mapping
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title or 'Untitled Quiz'}"


class BlacklistedToken(models.Model):
    """
    Model to store blacklisted JWT tokens.
    """
    token = models.TextField(unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Blacklisted Token'
        verbose_name_plural = 'Blacklisted Tokens'
        indexes = [
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        return f"Blacklisted token - {self.blacklisted_at}"
