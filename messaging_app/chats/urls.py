from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet
from chats.auth import CustomTokenObtainPairView, logout_view
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin

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

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', logout_view, name='logout'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
