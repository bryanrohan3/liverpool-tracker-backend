from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import *

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    username = serializers.CharField(source="user.username")
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password', 'token']

    def create(self, validated_data):
        # Extract user data
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        
        # Create the User
        user = User.objects.create_user(
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password=password
        )
        
        # Create the UserProfile
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        
        # Generate a token for the new user
        Token.objects.create(user=user)
        
        return user_profile

    def get_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj.user)
        return token.key


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'date_time_created']
        read_only_fields = ['from_user', 'date_time_created']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']