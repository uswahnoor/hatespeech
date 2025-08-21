from django.urls import path
from . import views

urlpatterns = [
    # Allow with and without trailing slash to avoid redirects on POST
    path('detect/', views.detect_hate_speech, name='detect_hate_speech'),
    path('detect', views.detect_hate_speech),

    # History endpoint (GET)
    path('detect/history/', views.get_history, name='get_history'),
    path('detect/history', views.get_history),
    
    # Public API documentation
    path('docs/', views.api_documentation, name='api_documentation'),
    path('docs', views.api_documentation),
    
    # HTML documentation page
    path('docs/html/', views.api_docs_html, name='api_docs_html'),
    path('docs/html', views.api_docs_html),
]
