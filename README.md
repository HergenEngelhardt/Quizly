# Quizly

Quizly is an intelligent quiz generation platform API built with Django REST Framework. It leverages AI technology to automatically generate quizzes from YouTube videos, allowing users to create educational content and test their knowledge through an interactive quiz system.

## Features

- **User authentication and authorization** - JWT token-based authentication with secure cookie handling
- **AI-powered quiz generation** - Automatically create quizzes from YouTube videos using OpenAI Whisper and Google Generative AI
- **Quiz management system** - Create, read, update, and delete quizzes
- **Video transcription** - Extract audio from YouTube videos and transcribe using Whisper
- **Question management** - Multiple-choice questions with customizable options
- **Quiz attempt tracking** - Track user quiz sessions and scores
- **Token blacklisting** - Secure logout with token invalidation
- **User-specific content** - Each user can only access their own quizzes

## Technology Stack

- **Backend**: Django 5.2.5, Django REST Framework 3.15.2
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Authentication**: JWT token-based authentication with SimpleJWT
- **AI Services**: OpenAI Whisper for transcription, Google Generative AI for quiz generation
- **Video Processing**: yt-dlp for YouTube audio extraction
- **Image Handling**: Pillow for media processing
- **Testing**: pytest, pytest-django, coverage
- **Code Quality**: Black formatter, Flake8 linter
- **Containerization**: Docker, Docker Compose
- **Production Database**: PostgreSQL with Docker support

## API Features

- RESTful API design
- UUID-based resource identification
- Comprehensive error handling
- Secure HTTP-only cookie authentication
- JSON response format
- Detailed API documentation

## Prerequisites

### For Local Development
- Python 3.8+
- Git
- Web browser
- YouTube API access (optional, for enhanced features)
- OpenAI API key (for AI features)
- Google AI API key (for quiz generation)

### For Docker Development (Recommended)
- Docker Desktop (installed and running)
- Docker Compose (included with Docker Desktop)
- Git
- Web browser
- OpenAI API key (for AI features)
- Google AI API key (for quiz generation)

**Note**: Docker Desktop provides a user-friendly interface to manage containers, view logs, and monitor your application. Make sure it's running before starting the project.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/HergenEngelhardt/Quizly.git
cd Quizly
```

### 2. Set up virtual environment

```bash
python -m venv .venv
```

**On Windows:**
```bash
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-ai-api-key
```

### 5. Database setup

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. (Optional) Load sample data

```bash
python manage.py loaddata fixtures/sample_data.json
```

## Running the Project

### Option 1: Local Development

#### Start the backend server

```bash
python manage.py runserver
```

The server will start at http://127.0.0.1:8000/

### Option 2: Docker (Recommended)

#### Prerequisites for Docker
- Docker Desktop installed and running
- Docker Compose installed (included with Docker Desktop)

#### Docker Desktop Setup
1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop/
2. **Start Docker Desktop** and ensure it's running (check system tray icon)
3. **Verify Docker installation**:
   ```bash
   docker --version
   docker-compose --version
   ```

#### Environment Setup for Docker

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-google-ai-api-key
POSTGRES_DB=quizly
POSTGRES_USER=quizly_user
POSTGRES_PASSWORD=quizly_password
```

#### Build and run with Docker Compose

```bash
# Ensure Docker Desktop is running first

# Build the Docker images
docker-compose build

# Start all services (web app + PostgreSQL database)
docker-compose up -d

# View logs to verify everything is working
docker-compose logs -f web

# Check if containers are running
docker-compose ps
```

#### Accessing Docker containers in Docker Desktop
1. Open Docker Desktop
2. Go to "Containers" tab
3. You should see your "quizly" project with two running containers:
   - `quizly-web-1` (Django application)
   - `quizly-db-1` (PostgreSQL database)
4. You can view logs, inspect, and manage containers directly from Docker Desktop UI

#### Initial setup with Docker

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser

# (Optional) Load sample data
docker-compose exec web python manage.py loaddata fixtures/sample_data.json
```

#### Docker service management

```bash
# Check container status
docker-compose ps

# Stop all services
docker-compose down

# Stop and remove volumes (caution: deletes database data)
docker-compose down -v

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d

# View real-time logs
docker-compose logs -f

# Access container shell (for debugging)
docker-compose exec web bash
docker-compose exec db psql -U quizly_user -d quizly
```

#### Troubleshooting Docker Issues

**If containers won't start:**
1. Ensure Docker Desktop is running
2. Check if ports 8000 and 5432 are available
3. View container logs: `docker-compose logs`

**If database connection fails:**
1. Wait for PostgreSQL to fully initialize (first run takes longer)
2. Check database logs: `docker-compose logs db`
3. Verify environment variables in `.env` file

**Performance issues:**
1. Allocate more resources to Docker Desktop (Settings → Resources)
2. Enable WSL 2 backend on Windows for better performance

The application will be available at http://127.0.0.1:8000/

### Access the application

- **API**: http://127.0.0.1:8000/api/
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **Frontend**: Connect your frontend application to the API endpoints

## API Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/register/` | POST | User registration | No |
| `/api/login/` | POST | User authentication | No |
| `/api/logout/` | POST | User logout | Yes |
| `/api/token/refresh/` | POST | Refresh access token | No |
| `/api/createQuiz/` | POST | Create quiz from YouTube URL | Yes |
| `/api/quizzes/` | GET | List user's quizzes | Yes |
| `/api/quizzes/{id}/` | GET | Get specific quiz | Yes |
| `/api/quizzes/{id}/` | PUT | Update quiz (full) | Yes |
| `/api/quizzes/{id}/` | PATCH | Update quiz (partial) | Yes |
| `/api/quizzes/{id}/` | DELETE | Delete quiz | Yes |

## API Usage Examples

### User Registration
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "securepassword"}'
```

### User Login
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepassword"}'
```

### Create Quiz from YouTube URL
```bash
curl -X POST http://127.0.0.1:8000/api/createQuiz/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### List User's Quizzes
```bash
curl -X GET http://127.0.0.1:8000/api/quizzes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Development

### Local Development Setup

Format code:
```bash
black .
```

Lint code:
```bash
flake8 .
```

### Docker Development

#### Testing with Docker
```bash
# Run tests in Docker container
docker-compose exec web pytest

# Run tests with coverage
docker-compose exec web pytest --cov=.

# Generate coverage report
docker-compose exec web coverage run -m pytest
docker-compose exec web coverage report
docker-compose exec web coverage html
```

#### Database operations with Docker
```bash
# Create new migration
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Access Django shell
docker-compose exec web python manage.py shell

# Access database shell
docker-compose exec db psql -U quizly_user -d quizly
```

#### Viewing Docker logs
```bash
# View web application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f db

# View all service logs
docker-compose logs -f
```

### Code Quality

### Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=.
```

Generate coverage report:
```bash
coverage run -m pytest
coverage report
coverage html 
```

### Database Operations

Create new migration:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```

Create superuser:
```bash
python manage.py createsuperuser
```

## Production Deployment

1. Set `DEBUG=False` in your environment
2. Configure proper database (PostgreSQL recommended)
3. Set up proper CORS settings for your frontend domain
4. Use environment variables for all sensitive data
5. Configure static file serving (e.g., nginx)
6. Set up proper logging
7. Use a production WSGI server (e.g., Gunicorn)
8. Configure SSL/HTTPS
9. Set up monitoring and error tracking

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/quizly_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-ai-api-key
```

## Troubleshooting

### Common Issues

- **Migration errors**: Run `python manage.py migrate --fake-initial`
- **Permission errors**: Ensure proper file permissions on database and media files
- **CORS errors**: Check CORS settings in `settings.py` and ensure frontend domain is allowed
- **API key errors**: Verify OpenAI and Google AI API keys are correctly set in environment variables
- **YouTube download errors**: Check yt-dlp version and update if necessary
- **Audio transcription errors**: Ensure Whisper model is properly installed and accessible

### Docker-specific Issues

- **Container won't start**: Check Docker logs with `docker-compose logs web`
- **Database connection errors**: Ensure PostgreSQL container is running with `docker-compose ps`
- **Port conflicts**: Change port mapping in `docker-compose.yml` if port 8000 is occupied
- **Volume mounting issues**: On Windows, ensure Docker has access to your drive
- **Build failures**: Try `docker-compose build --no-cache` to rebuild from scratch
- **Permission issues**: On Linux/macOS, check file permissions for Docker volumes

### Debug Mode

Enable debug mode for development:
```python
# In settings.py
DEBUG = True
```

Check logs for detailed error information:
```bash
# Local development
python manage.py runserver --verbosity=2

# Docker development
docker-compose logs -f web
```

### Performance Optimization

- Use database indexing for frequently queried fields
- Implement caching for expensive operations
- Optimize AI model calls by batching requests
- Use pagination for large result sets
- Consider using background tasks for video processing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the documentation above
- Review existing issues in the repository
- Create a new issue with detailed description
- Contact the development team

## Acknowledgments

- OpenAI for Whisper speech recognition
- Google for Generative AI services
- Django and Django REST Framework communities
- yt-dlp for YouTube video processing
- All contributors and testers
