# Custom Hate Speech Detection Model

This folder contains a custom-trained hate speech detection model.

## Model Files

- **model.safetensors** (255.4 MB) - The trained model weights in safetensors format
- **tokenizer.json** - Tokenizer configuration for text preprocessing
- **config.json** - Model configuration
- **tokenizer_config.json** - Tokenizer-specific configuration
- **special_tokens_map.json** - Special tokens mapping
- **vocab.txt** - Vocabulary file
- **model_info.json** - Metadata about the model

## Model Specifications

- **Architecture**: DistilBERT (Distilled BERT)
- **Type**: Sequence Classification
- **Input**: Text (up to 512 tokens)
- **Output**: Binary classification (Safe/Toxic)
- **Classes**:
  - 0: Safe content
  - 1: Toxic/Offensive content

## Usage

The model is automatically loaded by the `CustomHateSpeechClassifier` class:

```python
from Classifier.custom_classifier import CustomHateSpeechClassifier

classifier = CustomHateSpeechClassifier()
label, confidence = classifier.predict("Your text here")

# label: 0 (safe) or 1 (toxic)
# confidence: float between 0 and 1
```

## Integration

This model is integrated into the hate speech detection API through:
1. `custom_classifier.py` - Model loading and inference
2. `preprocessor.py` - Text preprocessing and detection pipeline
3. Backend API endpoints - HTTP endpoints for classification

## Performance

- **Confidence Calibration**: Confidence scores are reduced by 13% for realistic assessment
- **Processing**: GPU acceleration when available (CUDA), CPU fallback
- **Speed**: ~100-200ms per request on CPU

## Sharing

To share this model with others:
1. Copy the entire `custom_model` folder
2. Place it in the `Classifier` directory of their project
3. The model is self-contained and ready to use offline

## Requirements

- PyTorch (torch)
- Transformers library
- Python 3.8+

No internet connection required after model download.
