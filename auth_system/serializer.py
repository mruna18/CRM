from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
import re

class BlacklistTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        token = data.get("token")
        if not token:
            raise serializers.ValidationError("Token is required.")
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']

    def validate_username(self, value):
        """Validate username format (should be mobile number)"""
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Username must be a valid mobile number")
        return value

    def validate_email(self, value):
        """Validate email format"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        return value

    def validate(self, data):
        """Validate password confirmation"""
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)