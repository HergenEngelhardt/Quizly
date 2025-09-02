"""
Admin configuration for quiz app.
"""
from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, BlacklistedToken


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin interface for Quiz model.
    """
    list_display = ['title', 'user', 'created_at', 'questions_count']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def questions_count(self, obj):
        """
        Display number of questions for this quiz.
        """
        return obj.questions.count()
    questions_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for Question model.
    """
    list_display = ['question_title_short', 'quiz_title', 'created_at']
    list_filter = ['created_at', 'quiz__user']
    search_fields = ['question_title', 'quiz__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def question_title_short(self, obj):
        """
        Display shortened question title.
        """
        return obj.question_title[:50] + '...' if len(obj.question_title) > 50 else obj.question_title
    question_title_short.short_description = 'Question'
    
    def quiz_title(self, obj):
        """
        Display quiz title.
        """
        return obj.quiz.title or 'Untitled Quiz'
    quiz_title.short_description = 'Quiz'


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """
    Admin interface for QuizAttempt model.
    """
    list_display = ['user', 'quiz_title', 'score', 'completed_at', 'created_at']
    list_filter = ['completed_at', 'created_at', 'quiz__user']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def quiz_title(self, obj):
        """
        Display quiz title.
        """
        return obj.quiz.title or 'Untitled Quiz'
    quiz_title.short_description = 'Quiz'


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for BlacklistedToken model.
    """
    list_display = ['token_short', 'blacklisted_at']
    list_filter = ['blacklisted_at']
    readonly_fields = ['token', 'blacklisted_at']
    ordering = ['-blacklisted_at']
    
    def token_short(self, obj):
        """
        Display shortened token.
        """
        return obj.token[:50] + '...' if len(obj.token) > 50 else obj.token
    token_short.short_description = 'Token'
