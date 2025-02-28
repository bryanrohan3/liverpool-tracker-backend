from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class MatchesView(APIView):
    def get(self, request):
        team_id = request.query_params.get('teamId', 64)  
        url = f"https://api.football-data.org/v4/teams/{team_id}/matches?status=SCHEDULED"
        
        headers = {
            "X-Auth-Token": settings.FOOTBALL_API_KEY,
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return Response(response.json())
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class MatchesProxyView(APIView):
    def get(self, request, match_id):
        url = f"https://api.football-data.org/v4/matches/{match_id}"
        headers = {
            "X-Auth-Token": settings.FOOTBALL_API_KEY,
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserViewSet(
    mixins.CreateModelMixin,  # Enable POST requests to create users
    mixins.ListModelMixin,    # Enable GET requests to list users
    viewsets.GenericViewSet
):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Allow searching for users by username using `?search=username`.
        Exclude the authenticated user from the results.
        """
        search = self.request.query_params.get('search', '')
        if search:
            return UserProfile.objects.filter(user__username__icontains=search).exclude(user=self.request.user)
        return UserProfile.objects.exclude(user=self.request.user)
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated], url_path='current')
    def current(self, request):
        """
        Get the profile of the currently authenticated user.
        """
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserSerializer(user_profile)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated], url_path='send-friend-request')
    def send_friend_request(self, request, pk=None):
        """
        Send a friend request to another user.
        """
        to_user = self.get_object()
        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated], url_path='accept-friend-request')
    def accept_friend_request(self, request, pk=None):
        """
        Accept a friend request.
        """
        friend_request = FriendRequest.objects.filter(to_user=request.user, from_user_id=pk, status=FriendRequest.PENDING).first()
        if not friend_request:
            return Response({'error': 'No pending friend request found.'}, status=status.HTTP_404_NOT_FOUND)

        friend_request.status = FriendRequest.ACCEPTED
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated], url_path='decline-friend-request')
    def decline_friend_request(self, request, pk=None):
        """
        Decline a friend request.
        """
        friend_request = FriendRequest.objects.filter(to_user=request.user, from_user_id=pk, status=FriendRequest.PENDING).first()
        if not friend_request:
            return Response({'error': 'No pending friend request found.'}, status=status.HTTP_404_NOT_FOUND)

        friend_request.status = FriendRequest.REJECTED
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='login', permission_classes=[])
    def login(self, request):
        # Use the UserLoginSerializer to validate data
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            # Return a 400 Bad Request if the data is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate the user
        user = authenticate(username=username, password=password)
        
        if user:
            if not user.is_active:
                return Response({'error': 'This account is inactive.'}, status=status.HTTP_403_FORBIDDEN)
            
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(UserProfile.objects.get(user=user)).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        
        # Return 400 Bad Request if authentication fails
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)


class FlightsViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Flight.objects.all()
    serializer_class = FlightsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically associate the flight with the logged-in user.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Ensure users can only see their own flights.
        """
        return Flight.objects.filter(user=self.request.user)
    

class AttendingGameViewSet(mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = AttendingGame.objects.all()
    serializer_class = AttendingGameSerializer

    def perform_create(self, serializer):
        """
        Automatically associate the flight with the logged-in user.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Ensure users can only see their own flights.
        """
        return AttendingGame.objects.filter(user=self.request.user)