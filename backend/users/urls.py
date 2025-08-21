from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginView

urlpatterns = [
    # Signup (with and without trailing slash to avoid 301 redirects on preflight)
    path('signup/', views.signup, name='signup'),
    path('signup', views.signup),

    # Email verification
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    # Frontend calls /auth/verify-email/<token>
    path('verify-email/<str:token>/', views.verify_email),

    # Resend verification
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('resend-verification', views.resend_verification),

    # Login using JWT token obtain pair (aliases provided)
    path('login/', LoginView.as_view(), name='login'),
    path('login', LoginView.as_view()),

    # JWT direct endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/refresh', TokenRefreshView.as_view()),

    # User profile endpoints
    path('user/profile/', views.profile, name='user_profile'),
    path('user/profile', views.profile),
    # API key management
    path('api-keys/', views.list_api_keys, name='list_api_keys'),
    path('api-keys/create/', views.create_api_key, name='create_api_key'),
    path('api-keys/delete/<int:key_id>/', views.delete_api_key, name='delete_api_key'),
]
