from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import render
from .preprocess import get_preprocessor
from .model import predict_with_model
from .models import DetectionResult
from users.models import APIKey
import time

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    history = DetectionResult.objects.filter(user=request.user).order_by('-created_at')
    return Response([{
        'id': item.id,
        'text': item.text,
        'classification': item.classification,
        'confidence': item.confidence,
        'created_at': item.created_at,
    } for item in history])

@api_view(['POST'])
def detect_hate_speech(request):
    """
    Detect hate speech in text.
    
    Authentication: Requires valid API key in X-API-KEY header
    
    Request body:
    {
        "text": "Text to analyze"
    }
    
    Response:
    {
        "classification": "safe" | "toxic",
        "confidence": 0.95,
        "sentiment": "negative" | "positive" | "neutral",
        "engine": "transformer",
        "latency_ms": 150.2
    }
    """
    print(f"Detection request from IP: {request.META.get('REMOTE_ADDR')}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Get API key from header
    api_key = request.headers.get('X-API-KEY')
    print(f"Extracted API key: {api_key}")
    
    if not api_key:
        print("No API key provided")
        return Response({
            "error": "API key required in 'X-API-KEY' header.",
            "message": "To get an API key, register at our website and create one in your dashboard."
        }, status=401)
    
    # Find the API key and associated user
    try:
        api_key_obj = APIKey.objects.select_related('user').get(key=api_key)
        user = api_key_obj.user
        print(f"API key belongs to user: {user.email}")
    except APIKey.DoesNotExist:
        print("Invalid API key")
        return Response({
            "error": "Invalid API key.",
            "message": "Please check your API key or create a new one in your dashboard."
        }, status=403)

    text = request.data.get("text", "")
    if not text:
        return Response({"error": "Text is required"}, status=400)

    start = time.perf_counter()
    pre = get_preprocessor().preprocess(text)

    # Get prediction from the transformer model
    model_outcome = predict_with_model(pre["cleaned"])  # pass cleaned text
    if model_outcome is None:
        return Response({
            "error": "Model prediction failed"
        }, status=500)

    hate_label, confidence, sentiment = model_outcome
    classification = "toxic" if hate_label == 1 else "safe"
    engine = "transformer"
    
    latency_ms = (time.perf_counter() - start) * 1000.0
    
    # Save the detection result
    result = DetectionResult.objects.create(
        user=user,  # Use user from API key
        text=text,
        classification=classification,
        confidence=float(confidence),
        engine=engine,
        latency_ms=round(latency_ms, 2),
        preprocessed_text=pre["cleaned"]
    )
    
    return Response({
        "id": result.id,
        "classification": classification,
        "confidence": float(confidence),
        "sentiment": sentiment,
        "engine": engine,
        "latency_ms": round(latency_ms, 2),
        "text": text,
        "preprocessed": {
            "cleaned": pre["cleaned"],
            "tokens": pre["tokens"],
            "lemmas": pre["lemmas"],
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_documentation(request):
    """
    Public API documentation for external developers.
    """
    docs = {
        "name": "Hate Speech Detection API",
        "version": "1.0",
        "description": "AI-powered hate speech and toxicity detection API",
        "base_url": "http://localhost:8000/api",
        "authentication": {
            "type": "API Key",
            "header": "X-API-KEY",
            "description": "Get your API key by registering at our website"
        },
        "endpoints": {
            "/detect/": {
                "method": "POST",
                "description": "Detect hate speech in text",
                "headers": {
                    "Content-Type": "application/json",
                    "X-API-KEY": "your-api-key-here"
                },
                "request_body": {
                    "text": "string (required) - Text to analyze"
                },
                "response": {
                    "classification": "string - 'safe' or 'toxic'",
                    "confidence": "number - Confidence score (0-1)",
                    "sentiment": "string - 'positive', 'negative', or 'neutral'",
                    "engine": "string - AI model used",
                    "latency_ms": "number - Processing time in milliseconds"
                },
                "example_request": {
                    "text": "Hello, how are you today?"
                },
                "example_response": {
                    "classification": "safe",
                    "confidence": 0.95,
                    "sentiment": "positive",
                    "engine": "transformer",
                    "latency_ms": 145.2
                }
            },
            "/docs/": {
                "method": "GET",
                "description": "This documentation endpoint"
            }
        },
        "error_codes": {
            "400": "Bad Request - Missing or invalid text",
            "401": "Unauthorized - Missing API key",
            "403": "Forbidden - Invalid API key",
            "500": "Internal Server Error - Model processing failed"
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000
        },
        "getting_started": {
            "step_1": "Register an account at our website",
            "step_2": "Create an API key in your dashboard",
            "step_3": "Include the API key in X-API-KEY header",
            "step_4": "Send POST requests to /api/detect/"
        }
    }
    return Response(docs)


def api_docs_html(request):
    """
    HTML documentation page for external developers.
    """
    return render(request, 'api_docs.html')
