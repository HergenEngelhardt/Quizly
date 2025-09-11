# Database Setup Guide

This guide explains the different database options for the Quizly project.

## TL;DR - Quick Start

**For beginners**: Use SQLite (Option 1) - it's the easiest!

1. Copy `.env.example` to `.env`
2. Make sure `FORCE_SQLITE=true` is in your `.env` file
3. Run `python manage.py migrate`
4. Done! ✅

## Option 1: SQLite (Recommended for Local Development)

### What is SQLite?
- Simple file-based database
- No installation required
- Perfect for development and testing
- Database stored in `db.sqlite3` file

### Setup Steps:
1. **Create your .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit your .env file to include:**
   ```env
   FORCE_SQLITE=true
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   GEMINI_API_KEY=your-google-ai-key-here
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Verify setup:**
   - You should see a `db.sqlite3` file in your project root
   - Run `python manage.py check` - should show no errors

### Advantages:
- ✅ No database software to install
- ✅ Works immediately
- ✅ Great for learning and development
- ✅ Easy backup (just copy the db.sqlite3 file)

### Disadvantages:
- ❌ Not suitable for production
- ❌ No concurrent user support
- ❌ Limited advanced features

## Option 2: PostgreSQL with Docker (Recommended for Production-like Development)

### What is PostgreSQL with Docker?
- Professional database system
- Runs in isolated Docker container
- Same database as used in production

### Prerequisites:
- Docker Desktop installed and running
- Basic Docker knowledge helpful

### Setup Steps:
1. **Make sure Docker is running:**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Edit .env.docker (not .env!):**
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-google-ai-key-here
   DATABASE_URL=postgres://quizly_user:quizly_password@db:5432/quizly
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Advantages:
- ✅ Production-like environment
- ✅ Better for team development
- ✅ Advanced database features
- ✅ Easy to reset/rebuild

### Disadvantages:
- ❌ Requires Docker knowledge
- ❌ Uses more system resources
- ❌ More complex setup

## Option 3: Local PostgreSQL Installation (Advanced)

### What is Local PostgreSQL?
- PostgreSQL installed directly on your system
- Full control over database configuration
- No Docker required

### Prerequisites:
- PostgreSQL installed on your system
- Knowledge of PostgreSQL administration

### Setup Steps:
1. **Install PostgreSQL:**
   - Windows: Download from postgresql.org
   - macOS: `brew install postgresql`
   - Linux: `sudo apt install postgresql`

2. **Create database and user:**
   ```sql
   CREATE DATABASE quizly_db;
   CREATE USER quizly_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE quizly_db TO quizly_user;
   ```

3. **Edit your .env file:**
   ```env
   # Remove or comment out FORCE_SQLITE
   # FORCE_SQLITE=true
   
   DATABASE_URL=postgres://quizly_user:your_password@localhost:5432/quizly_db
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   GEMINI_API_KEY=your-google-ai-key-here
   ```

4. **Install PostgreSQL adapter:**
   ```bash
   pip install psycopg2-binary
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

### Advantages:
- ✅ Full control over database
- ✅ Production-like without Docker
- ✅ Best performance for local development

### Disadvantages:
- ❌ Complex installation
- ❌ System-wide installation
- ❌ Requires PostgreSQL knowledge

## Switching Between Database Options

### From SQLite to PostgreSQL:
1. Backup your data: `python manage.py dumpdata > backup.json`
2. Switch your .env configuration
3. Run migrations: `python manage.py migrate`
4. Load data: `python manage.py loaddata backup.json`

### From PostgreSQL to SQLite:
1. Backup your data: `python manage.py dumpdata > backup.json`
2. Add `FORCE_SQLITE=true` to your .env
3. Remove/comment out DATABASE_URL
4. Run migrations: `python manage.py migrate`
5. Load data: `python manage.py loaddata backup.json`

## Troubleshooting

### SQLite Issues:
- **No db.sqlite3 file**: Run `python manage.py migrate`
- **Permission errors**: Check file permissions in project directory
- **Database locked**: Make sure no other Django process is running

### PostgreSQL Issues:
- **Connection refused**: Check if PostgreSQL is running
- **Authentication failed**: Verify username/password in .env
- **Database does not exist**: Create the database first

### Docker Issues:
- **Container won't start**: Check if Docker Desktop is running
- **Port conflicts**: Make sure ports 8000 and 5432 are free
- **Build failures**: Try `docker-compose build --no-cache`

## Which Option Should I Choose?

| Use Case | Recommended Option |
|----------|-------------------|
| Learning Django | SQLite (Option 1) |
| Local development | SQLite (Option 1) |
| Team development | Docker PostgreSQL (Option 2) |
| Production-like testing | Docker PostgreSQL (Option 2) |
| Advanced database features | Local PostgreSQL (Option 3) |
| CI/CD pipeline | Docker PostgreSQL (Option 2) |

## Need Help?

If you're having database issues:
1. Check this guide first
2. Look at the main README.md troubleshooting section
3. Make sure your .env file is configured correctly
4. Try the SQLite option if PostgreSQL is causing problems

Remember: **SQLite is perfect for getting started!** You can always switch to PostgreSQL later when you need more advanced features.
