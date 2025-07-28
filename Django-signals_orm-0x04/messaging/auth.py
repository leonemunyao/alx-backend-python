from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from .serializers import UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token that returns user information along with the tokens."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
            if user:
                user_serializer = UserSerializer(user)
                response.data['user'] = user_serializer.data
        return response

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """Endpoint to log out a user by blacklisting their token."""
    try:
        token = request.data.get('token')
        if not token:
            return Response({"detail": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Blacklist the token
        RefreshToken(token).blacklist()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
