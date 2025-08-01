from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet
from messaging.auth import CustomTokenObtainPairView, logout_view
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from . import views

# Create a router and register our viewsets
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

# Create nested router for messages within conversations
conversations_router = nested_routers.NestedDefaultRouter(
    router, 
    r'conversations', 
    lookup='conversation'
)
conversations_router.register(
    r'messages', 
    MessageViewSet, 
    basename='conversation-messages'
)

app_name = 'messaging'

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('messages/<int:message_id>/edit/', views.message_edit, name='message_edit'),
    path('messages/<int:message_id>/history/', views.message_edit_history, name='message_edit_history'),
    path('user/delete', views.delete_user, name='delete_user'),
    path('logout/', logout_view, name='logout'),
]
