"""
Custom Hate Speech Classifier using a trained DistilBERT model.
This classifier uses a proprietary trained model for offensive language detection.
"""

import torch
import json
import os
from pathlib import Path

logger_enabled = False

def log(msg):
    if logger_enabled:
        print(f"[CustomClassifier] {msg}")


class CustomHateSpeechClassifier:
    """Custom-trained hate speech detection model."""
    
    def __init__(self, model_dir=None):
        """
        Initialize the custom hate speech classifier.
        
        Args:
            model_dir: Path to directory containing model files (model.safetensors)
        """
        if model_dir is None:
            # Default to custom_model folder in Classifier directory
            model_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "custom_model"
            )
        
        self.model_dir = model_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        log(f"Using device: {self.device}")
        log(f"Model directory: {self.model_dir}")
        
        try:
            self._load_model()
            log("Custom classifier loaded successfully")
        except Exception as e:
            log(f"Error loading classifier: {e}")
            raise
    
    def _load_model(self):
        """Load the model from safetensors"""
        try:
            from transformers import AutoModelForSequenceClassification
            
            # Load model from local directory (safetensors format)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_dir
            )
            
            self.model.to(self.device)
            self.model.eval()
            log("Model loaded successfully")
        except Exception as e:
            log(f"Error loading model: {e}")
            raise
    
    def predict(self, text):
        """
        Predict if text contains hate speech.
        
        Args:
            text (str): Text to classify
            
        Returns:
            tuple: (label, confidence)
                - label: 1 for hate speech/offensive, 0 for safe
                - confidence: float between 0 and 1
        """
        try:
            from transformers import AutoTokenizer
            
            # Load tokenizer on demand (from Hugging Face cache or download)
            # This avoids issues with local tokenizer files
            tokenizer = AutoTokenizer.from_pretrained(
                "distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            # Tokenize the input
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=1)
            
            # Get the predicted class and confidence
            predicted_class = torch.argmax(logits, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Reverse the label (flip: 1->0, 0->1)
            label = 1 - predicted_class
            
            # Reduce confidence by 13% to account for model calibration
            adjusted_confidence = max(0.0, min(1.0, confidence - 0.13))
            
            return label, adjusted_confidence
            
        except Exception as e:
            log(f"Error during prediction: {e}")
            raise
