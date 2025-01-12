from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import viewsets
from django.contrib import admin

# Define the router for standard CRUD endpoints
api_router = DefaultRouter()
api_router.register(r'users', viewsets.UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_router.urls)),
    path('api/matches/', viewsets.MatchesView.as_view(), name='matches'),  # Added .as_view() here
    path('api/proxy/matches/<int:match_id>/', viewsets.MatchesProxyView.as_view(), name='matches-proxy'),
]

urlpatterns += api_router.urls
