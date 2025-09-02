# REFACTORING PLAN für Clean Code Compliance

## 1. Funktionen > 14 Zeilen aufteilen

### quiz_app/utils.py

#### generate_quiz_from_transcript() (67 Zeilen → 4 Funktionen):
```python
def configure_gemini_model():
    """Configure and return Gemini AI model."""
    
def create_quiz_prompt(transcript, video_title):
    """Create prompt for Gemini AI."""
    
def parse_quiz_response(response_text):
    """Parse and validate Gemini AI response."""
    
def validate_quiz_structure(quiz_data):
    """Validate quiz data structure."""
```

#### download_youtube_audio() (28 Zeilen → 3 Funktionen):
```python
def create_ydl_options(output_file):
    """Create yt-dlp options configuration."""
    
def extract_audio_file(url, ydl_opts):
    """Extract audio using yt-dlp."""
    
def verify_audio_file(temp_dir):
    """Verify audio file exists and return path."""
```

### quiz_app/api/views.py

#### create_quiz_view() (68 Zeilen → 4 Funktionen):
```python
def validate_quiz_creation_data(request):
    """Validate request data for quiz creation."""
    
def process_video_transcription(url):
    """Process video URL to transcript."""
    
def create_quiz_from_data(user, url, quiz_data, video_info):
    """Create quiz object from processed data."""
    
def cleanup_quiz_creation(audio_file_path):
    """Cleanup temporary files after quiz creation."""
```

## 2. Test-Konfiguration reparieren

### conftest.py korrigieren:
```python
import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner

def pytest_configure(config):
    """Configure pytest for Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    settings.DEBUG = False
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
```

## 3. Fehlende Requirements ergänzen:
- pytest-cov==4.0.0
- pytest-django==4.9.0

## 4. Missing User Stories implementieren:
- User Story 7: Sidebar mit Heute/7-Tage Filter
- User Story 8: Quiz-Spiellogik mit Fortschritt
- User Story 9: Quiz-Auswertung mit Scoring
- User Story 10: Impressum/Datenschutz

## Priorität:
1. **HOCH**: Funktionen aufteilen (Clean Code)
2. **HOCH**: Tests reparieren (Coverage)
3. **MITTEL**: Fehlende User Stories
4. **NIEDRIG**: Frontend-Integration
