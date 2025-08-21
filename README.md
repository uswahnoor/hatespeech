# SafeSpeak Sentinel

## Overview

SafeSpeak Sentinel is a comprehensive web application designed to detect and prevent hate speech and harmful content. It combines powerful machine learning models with a user-friendly interface to help create safer online spaces.

## Project Structure

The project is divided into two main components:

### Frontend (`/frontend`)
- React-based web interface
- Built with TypeScript and Vite
- Uses Tailwind CSS and shadcn/ui for styling
- Features:
  - User authentication
  - Real-time content analysis
  - History tracking
  - User profile management

### Backend (`/backend`)
- Django-based REST API
- Machine learning models for content analysis
- Features:
  - JWT authentication
  - Content preprocessing and analysis
  - User management
  - History tracking
  - API endpoints for content detection

## Getting Started

### Prerequisites
- Node.js (LTS version)
- Python 3.12 or higher
- MySQL

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows:
.\env\Scripts\activate
# On Unix or MacOS:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend: http://localhost:8000

## Technology Stack

### Frontend
- **React** - Frontend framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - UI component library
- **React Router** - Client-side routing
- **React Query** - Data fetching and state management

### Backend
- **Django** - Web framework
- **Django REST Framework** - API development
- **JWT** - Authentication
- **MySQL** - Database
- **NLTK & spaCy** - Natural Language Processing
- **Python** - Programming language

## API Documentation

The backend API provides the following main endpoints:

- `/api/auth/` - Authentication endpoints
- `/api/detect/` - Content analysis endpoints
- `/api/history/` - Analysis history endpoints
- `/api/users/` - User management endpoints

Detailed API documentation is available at `/api/docs/` when running the backend server.

## Development

### Code Style
- Frontend follows TypeScript best practices
- Backend follows PEP 8 guidelines
- Use meaningful variable and function names
- Include comments for complex logic

### Testing
Both frontend and backend include test suites:
```bash
# Frontend tests
cd frontend
npm run test

# Backend tests
cd backend
python manage.py test
```

### Building for Production

#### Frontend
```bash
cd frontend
npm run build
```
This will create a `dist` directory with compiled assets.

#### Backend
```bash
cd backend
python manage.py collectstatic
```
Make sure to set `DEBUG=False` in production.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.