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

        # Check if the username already exists
        if User.objects.filter(username=user_data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})

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

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class FlightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['id', 'game_id', 'user', 'airline', 'departure_airport', 'arrival_airport', 'departure_time', 'departure_date', 'is_return', 'return_time', 'return_date', 'is_active']
        read_only_fields = ['user']

    def validate(self, data):
        """
        Custom validation to ensure that if `is_return` is True, return time and date are provided.
        """
        if data.get('is_return', False):
            if not data.get('return_time') or not data.get('return_date'):
                raise ValidationError("Return time and date must be provided when is_return is True.")
        else:
            # Ensure return_time and return_date are not set if is_return is False
            if data.get('return_time') or data.get('return_date'):
                raise ValidationError("Return time and date should not be provided when is_return is False.")

        return data

    def create(self, validated_data):
        # Automatically set the user to the currently authenticated user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Automatically set the user to the currently authenticated user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().update(instance, validated_data)

class AttendingGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendingGame
        fields = ['id', 'user', 'game_id']
        read_only_fields = ['user']

    def create(self, validated_data):
        # Automatically set the user to the currently authenticated user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
    
