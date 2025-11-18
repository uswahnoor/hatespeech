from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.conf import settings
from .models import User, APIKey, PasswordResetToken
from .serializers import RegisterSerializer, ProfileSerializer, APIKeySerializer, ForgotPasswordSerializer, ResetPasswordSerializer
import uuid
import secrets

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


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Send password reset email"""
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Invalidate existing tokens
            PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Create new reset token
            token = secrets.token_urlsafe(32)
            PasswordResetToken.objects.create(user=user, token=token)
            
            # Send reset email
            reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/auth/reset-password/{token}"
            try:
                send_mail(
                    "Reset Your Password",
                    f"Click here to reset your password: {reset_link}\n\nThis link will expire in 1 hour.",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send password reset email: {e}")
                # Continue anyway - don't reveal email sending issues
                pass
                
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            pass
        
        return Response({
            'message': 'If an account with that email exists, we sent a password reset link.'
        })
    
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using token"""
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return Response({
                    'error': 'Invalid or expired reset token.'
                }, status=400)
            
            # Reset password
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            return Response({
                'message': 'Password has been reset successfully.'
            })
            
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Invalid or expired reset token.'
            }, status=400)
    
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_reset_token(request, token):
    """Validate if reset token is still valid"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if reset_token.is_valid():
            return Response({
                'valid': True,
                'email': reset_token.user.email
            })
        else:
            return Response({
                'valid': False,
                'error': 'Token has expired or been used.'
            }, status=400)
            
    except PasswordResetToken.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Invalid token.'
        }, status=400)
