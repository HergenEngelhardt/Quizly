# Quizly - My First AI Quiz Project! 

Hey! This is my quiz project that I built with Django. It takes YouTube videos and automatically creates quizzes from them - pretty cool, right? 

The idea came to me because when learning from YouTube videos, I always forgot what I had watched. So I thought: "Why not just automatically create quizzes?" 

## What can my app do?

- **Users can sign up** - Everyone has their own quizzes
- **AI does all the work** - YouTube link in, quiz comes out!
- **Manage quizzes** - Create, view, edit, delete
- **Extract audio from videos** - The AI does this for me
- **Multiple-choice questions** - Like in school, but better
- **Track quiz attempts** - Who did what and how well
- **Secure logout** - Tokens are properly deleted
- **Everyone only sees their own stuff** - Privacy first!

## What I used (my tech list)

- **Backend**: Django 5.2.5 (the framework), Django REST Framework 3.15.2 (for the API)
- **Database**: SQLite (for testing), PostgreSQL (for "real" applications)
- **Login System**: JWT Tokens (sounds fancy, but it's just secure login)
- **AI Stuff**: OpenAI Whisper (converts speech to text), Google AI (makes the quiz questions)
- **Video Download**: yt-dlp (downloads YouTube audio)
- **Images**: Pillow (in case I need images someday)
- **Tests**: pytest (so I know if everything works)
- **Code formatting**: Black (formats code), Flake8 (finds errors)
- **Containers**: Docker (so it runs on everyone's computer)
- **Real Database**: PostgreSQL with Docker

## How my API works

- REST API (that means it follows certain rules)
- Each resource has a unique ID
- Errors are handled properly
- Secure cookies for login
- Everything comes back as JSON
- I tried to document everything

## What you need to get it running

### If you want to run it locally
- Python 3.8 or newer
- Git (to get the code)
- A web browser
- **FFMPEG** (needed for audio processing - see below!)
- YouTube API access (optional, for more features)
- OpenAI API Key (for AI features)
- Google AI API Key (for quiz creation)

#### Installing FFMPEG (important!)

**Windows - Option 1: Download**
1. Go to: https://ffmpeg.org/download.html
   - Best to take Windows builds from gyan.dev or BtbN
2. Extract ZIP file to `C:\ffmpeg`
3. Add the path to environment variables:
   - Right-click "This PC" → "Properties" → "Advanced System Settings"
   - "Environment Variables..." → In Path add `C:\ffmpeg\bin`

**Windows - Option 2: Command Line (easier)**
```powershell
winget install --id Gyan.FFmpeg -e --source winget
```

**macOS (for Mac users)**
1. Install Homebrew (if not already there):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install FFmpeg:
   ```bash
   brew install ffmpeg
   ```

**Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install ffmpeg
```

### If you use Docker (I recommend this!)
- Docker Desktop (installed and running)
- Docker Compose (comes with Docker Desktop)
- Git
- A web browser  
- OpenAI API Key
- Google AI API Key

**Important**: With Docker you don't need to install FFMPEG yourself - Docker does it for you!

**Tip**: Docker Desktop is super handy. You can look at containers, read logs, and manage everything. Make sure it's running before you start.

## How to install my project

### 1. Get the code

```bash
git clone https://github.com/HergenEngelhardt/Quizly.git
cd Quizly
```

### 2. Set up Python environment (Virtual Environment)

This is important so packages don't mix with other projects:

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

### 3. Install all required packages

```bash
pip install -r requirements.txt
```

### 4. Create configuration file

Create a `.env` file in the main folder and add your API keys:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-ai-key
```

### 5. Prepare database

```bash
python manage.py migrate
```

### 6. Create admin user

```bash
python manage.py createsuperuser
```

## How to start my project

### Option 1: Locally on your computer

#### Start backend server

```bash
python manage.py runserver
```

Then go to: http://127.0.0.1:8000/

### Option 2: With Docker (I prefer this!)

#### What you need for Docker
- Docker Desktop must be installed and started
- Docker Compose (comes with Docker Desktop)

#### Docker Desktop Setup
1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop/
2. **Start Docker Desktop** (look for the icon in the taskbar)
3. **Test if everything works**:
   ```bash
   docker --version
   docker-compose --version
   ```

#### Configuration for Docker

Create a `.env` file in the main folder:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-google-ai-key
POSTGRES_DB=quizly
POSTGRES_USER=quizly_user
POSTGRES_PASSWORD=quizly_password
```

#### Build and start with Docker Compose

```bash
# First check if Docker Desktop is running!

# Build Docker images
docker-compose build

# Start everything (web app + PostgreSQL database)
docker-compose up -d

# Look at logs to see if everything works
docker-compose logs -f web

# Check if containers are running
docker-compose ps
```

#### Look at Docker Desktop
1. Open Docker Desktop
2. Click on "Containers"
3. You should see your "quizly" project with two running containers:
   - `quizly-web-1` (Django app)
   - `quizly-db-1` (PostgreSQL database)
4. You can view logs and manage containers directly in Docker Desktop

#### Initial setup with Docker

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create admin user
docker-compose exec web python manage.py createsuperuser
```

#### Managing Docker containers

```bash
# Check container status
docker-compose ps

# Stop everything
docker-compose down

# Stop and delete database (careful!)
docker-compose down -v

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d

# Watch live logs
docker-compose logs -f

# Look inside containers (for debugging)
docker-compose exec web bash
docker-compose exec db psql -U quizly_user -d quizly
```

#### When Docker doesn't work

**Containers won't start:**
1. Docker Desktop must be running
2. Ports 8000 and 5432 must be free
3. Check logs: `docker-compose logs`

**Database connection doesn't work:**
1. PostgreSQL needs some time on first start
2. Check database logs: `docker-compose logs db`
3. Check your `.env` file again

**Runs slowly:**
1. Give Docker Desktop more RAM (Settings → Resources)
2. On Windows: Enable WSL 2

The app will run at: http://127.0.0.1:8000/

### Where to find the app

- **API**: http://127.0.0.1:8000/api/
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **Frontend**: Connect your frontend to the API endpoints

## My API endpoints (for other developers)

| URL | Method | What it does | Login needed? |
|-----|--------|--------------|---------------|
| `/api/register/` | POST | Create new user | No |
| `/api/login/` | POST | Login | No |
| `/api/logout/` | POST | Logout | Yes |
| `/api/token/refresh/` | POST | Refresh token | No |
| `/api/createQuiz/` | POST | Create quiz from YouTube URL | Yes |
| `/api/quizzes/` | GET | Show all your quizzes | Yes |
| `/api/quizzes/{id}/` | GET | Show specific quiz | Yes |
| `/api/quizzes/{id}/` | PUT | Edit quiz completely | Yes |
| `/api/quizzes/{id}/` | PATCH | Edit quiz partially | Yes |
| `/api/quizzes/{id}/` | DELETE | Delete quiz | Yes |

## Examples of how to use my API

### Create new user
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "securepassword"}'
```

### Login
### Create Quiz from YouTube URL
```bash
curl -X POST http://127.0.0.1:8000/api/createQuiz/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### List Your Quizzes
```bash
curl -X GET http://127.0.0.1:8000/api/quizzes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Development (for nerds like me)

### Local Development Setup

Format code (make it pretty):
```bash
black .
```

Check for errors:
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

## Production Deployment (when it gets serious)

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

## When things go wrong (Troubleshooting)

### Common Issues

- **Migration errors**: Run `python manage.py migrate --fake-initial`
- **Permission errors**: Make sure files have proper permissions
- **CORS errors**: Check CORS settings and make sure your frontend domain is allowed
- **API key errors**: Double-check your OpenAI and Google AI API keys
- **YouTube download errors**: Update yt-dlp if it's old
- **Audio transcription errors**: Make sure Whisper is properly installed

### Docker-specific Issues

- **Container won't start**: Check logs with `docker-compose logs web`
- **Database connection errors**: Make sure PostgreSQL container is running with `docker-compose ps`
- **Port conflicts**: Change port in `docker-compose.yml` if 8000 is taken
- **Volume mounting issues**: On Windows, make sure Docker can access your drive
- **Build failures**: Try `docker-compose build --no-cache` to start fresh
- **Permission issues**: On Linux/macOS, check file permissions

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

### Performance Tips (making it faster)

- Use database indexing for stuff you search a lot
- Cache expensive operations
- Optimize AI model calls by batching requests
- Use pagination for large result sets
- Consider using background tasks for video processing

## Contributing (if you want to help)

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome-feature`)
5. Open a Pull Request

## Support (when you need help)

For issues and questions:
- Check this documentation first
- Look at existing issues in the repository
- Create a new issue with detailed description
- Contact me if needed

## Thank you!

- OpenAI for Whisper speech recognition
- Google for Generative AI services
- Django and Django REST Framework communities
- yt-dlp for YouTube video processing
- Django and Django REST Framework communities
- OpenAI for Whisper
- Google for their AI services
- yt-dlp developers
- All contributors and testers

Thanks for checking out my project! 🚀
