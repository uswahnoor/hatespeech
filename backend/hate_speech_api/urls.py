from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from users.views import profile as user_profile_view

def api_root(request):
    return JsonResponse({
        'message': 'Welcome to Hate Speech Detection API',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'detect': '/api/detect/',
        }
    })

def favicon(request):
    return HttpResponse(status=204)  # No content for favicon

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api_root'),
    path('favicon.ico', favicon, name='favicon'),
    path('api/auth/', include('users.urls')),
    path('api/', include('detection.urls')),
    # User profile endpoint expected by frontend
    path('api/user/profile/', user_profile_view, name='user_profile'),
    path('api/user/profile', user_profile_view),
]
