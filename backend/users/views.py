from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.conf import settings
from .models import User, APIKey
from .serializers import RegisterSerializer, ProfileSerializer, APIKeySerializer
import uuid

signer = Signer()

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = signer.sign(user.email)
        # Align verification route with frontend: /auth/verify-email/:token
        verify_link = f"{settings.FRONTEND_URL.rstrip('/')}/auth/verify-email/{token}"
        try:
            send_mail(
                "Verify your account",
                f"Click here: {verify_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except Exception:
            # Do not fail signup if email sending has issues; the user can try verifying later
            pass
        return Response({"message": "User registered. Please verify your email."}, status=201)
    return Response(serializer.errors, status=400)

from rest_framework import status
from rest_framework.decorators import action
import uuid

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    try:
        email = signer.unsign(token)
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()
        return Response({"message": "Email verified successfully"})
    except BadSignature:
        return Response({"error": "Invalid or expired link"}, status=400)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        full_name = (f"{request.user.first_name} {request.user.last_name}").strip()
        data = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "name": full_name,
        }
        return Response(data)
    # PUT
    serializer = ProfileSerializer(instance=request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        # Optional password change
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])
        full_name = (f"{user.first_name} {user.last_name}").strip()
        return Response({
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "name": full_name,
        })
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_api_keys(request):
    keys = APIKey.objects.filter(user=request.user)
    serializer = APIKeySerializer(keys, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_api_key(request):
    if APIKey.objects.filter(user=request.user).count() >= 2:
        return Response({'error': 'Maximum 2 API keys allowed.'}, status=status.HTTP_400_BAD_REQUEST)
    key = str(uuid.uuid4())
    api_key = APIKey.objects.create(user=request.user, key=key)
    serializer = APIKeySerializer(api_key)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_api_key(request, key_id):
    try:
        api_key = APIKey.objects.get(id=key_id, user=request.user)
        api_key.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except APIKey.DoesNotExist:
        return Response({'error': 'API key not found.'}, status=status.HTTP_404_NOT_FOUND)

class VerifiedTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Block login if the user has not verified their email
        if not getattr(self.user, 'is_verified', False):
            raise serializers.ValidationError({
                'detail': 'Please verify your email before logging in.'
            })
        return data


class LoginView(TokenObtainPairView):
    serializer_class = VerifiedTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    email = (request.data.get('email') or '').strip().lower()
    if not email:
        return Response({
            'message': 'Email is required.'
        }, status=400)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Do not reveal whether the email exists
        return Response({
            'message': 'If an account with that email exists, we sent a verification email.'
        })

    if getattr(user, 'is_verified', False):
        return Response({
            'message': 'This account is already verified.'
        })

    token = signer.sign(user.email)
    verify_link = f"{settings.FRONTEND_URL.rstrip('/')}/auth/verify-email/{token}"
    try:
        send_mail(
            'Verify your account',
            f'Click here: {verify_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        pass

    return Response({
        'message': 'If an account with that email exists, we sent a verification email.'
    })
