from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import UserProfile
from .serializers import UserSerializer, UserLoginSerializer
import requests
from django.conf import settings
from rest_framework.views import APIView

class MatchesView(APIView):
    def get(self, request):
        team_id = request.query_params.get('teamId', 64)  # Default to team 64 if no teamId is provided
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

class UserViewSet(viewsets.GenericViewSet, 
                  mixins.CreateModelMixin, 
                  mixins.ListModelMixin, 
                  mixins.UpdateModelMixin, 
                  mixins.RetrieveModelMixin):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

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
                # Return 403 Forbidden if the account is inactive
                return Response({'error': 'This account is inactive.'}, status=status.HTTP_403_FORBIDDEN)
            
            # Retrieve or create a token for the authenticated user
            token, _ = Token.objects.get_or_create(user=user)
            # Return the token and user data in a successful response
            return Response({
                'message': 'Login successful',
                # 'user': UserSerializer(UserProfile.objects.get(user=user)).data,
                # 'token': token.key
            }, status=status.HTTP_200_OK)
        
        # Return 400 Bad Request if authentication fails
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
