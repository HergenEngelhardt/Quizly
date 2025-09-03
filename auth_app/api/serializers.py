"""
Simple serializers for user authentication.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new user accounts.

    Validates username, email uniqueness and password strength.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_email(self, value):
        """
        Check if email already exists.

        Args:
            value (str): Email address to validate

        Returns:
            str: Validated email address

        Raises:
            ValidationError: If email already exists
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_username(self, value):
        """
        Check if username already exists.

        Args:
            value (str): Username to validate

        Returns:
            str: Validated username

        Raises:
            ValidationError: If username already exists
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        """
        Create new user with hashed password.

        Args:
            validated_data (dict): Validated user data

        Returns:
            User: Created user object

        Raises:
            None
        """
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login authentication.

    Validates username and password credentials.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate user login credentials.

        Args:
            attrs (dict): Username and password data

        Returns:
            dict: Validated data with authenticated user

        Raises:
            ValidationError: If credentials are invalid or user is inactive
        """
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Username and password required.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data in API responses.

    Returns basic user information without sensitive data.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id",)
