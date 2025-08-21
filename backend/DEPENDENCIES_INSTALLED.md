# Backend Dependencies Installation Notes

## Missing Dependencies Summary

The following dependencies were missing from the virtual environment and have been installed:

### Core Framework Dependencies
- Django 4.1.13 (downgraded from 5.0 due to djongo compatibility)
- djangorestframework 3.14.0
- django-cors-headers 4.3.1
- djangorestframework-simplejwt 5.3.1
- drf-yasg 1.21.7

### Configuration
- python-decouple 3.8
- python-dotenv 1.0.0

### Machine Learning & NLP
- nltk 3.8.1
- spacy 3.7.2
- scikit-learn 1.3.2
- numpy 1.26.2
- pandas 2.1.4
- transformers 4.55.3 (upgraded from 4.36.1)
- tokenizers 0.21.4 (upgraded from 0.15.0)
- torch 2.5.1 (upgraded from 2.1.2)

### Database
- mysqlclient 2.2.1
- djongo 1.3.6
- pymongo 4.5.0

### Development & Testing
- black 23.12.1
- flake8 7.0.0
- pytest 7.4.3
- pytest-django 4.7.0

### Production
- gunicorn 21.2.0
- whitenoise 6.6.0

### Additional Required Dependencies
- huggingface-hub 0.34.4
- safetensors 0.6.2
- regex 2025.7.34
- requests 2.32.5

### spaCy Language Model
- en_core_web_sm 3.7.1 (downloaded and installed)

## Installation Issues Resolved

1. **tokenizers 0.15.0 compilation error**: Resolved by installing newer version (0.21.4) that comes with transformers
2. **torch 2.1.2 not available**: Upgraded to 2.5.1
3. **Django version conflict**: Downgraded to 4.1.13 for djongo compatibility
4. **Missing spaCy language model**: Downloaded en_core_web_sm 3.7.1

## Dependencies Status

✅ All dependencies are now installed and working
✅ Django server can start
✅ Hate speech detection model loads successfully
✅ spaCy English language model is available

## Next Steps

To activate the environment and run the server:
```powershell
cd F:\HatespeechProj\hatespeech\backend
.\env\Scripts\Activate.ps1
python manage.py runserver
```
