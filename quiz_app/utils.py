"""
Utility functions for quiz processing.
"""
import os
import tempfile
import yt_dlp
import whisper
import google.generativeai as genai
from django.conf import settings
from urllib.parse import urlparse, parse_qs
import json
import re


def extract_youtube_id(url):
    """
    Extract YouTube video ID from URL.
    """
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    
    return None


def download_youtube_audio(url):
    """
    Download YouTube video as audio file.
    """
    try:
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, 'audio.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # Return path to downloaded audio file
        audio_file = os.path.join(temp_dir, 'audio.wav')
        if os.path.exists(audio_file):
            return audio_file
        else:
            raise Exception("Audio file not found after download")
            
    except Exception as e:
        raise Exception(f"Error downloading YouTube audio: {str(e)}")


def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Whisper AI.
    """
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file_path)
        return result["text"]
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")


def generate_quiz_from_transcript(transcript, video_title=""):
    """
    Generate quiz from transcript using Gemini AI.
    """
    try:
        # Configure Gemini AI
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Erstelle ein Quiz mit genau 10 Fragen basierend auf dem folgenden Transkript eines YouTube-Videos.

        Video Titel: {video_title}
        Transkript: {transcript}

        Bitte erstelle das Quiz im folgenden JSON-Format:
        {{
            "title": "Quiz Titel basierend auf dem Inhalt",
            "description": "Kurze Beschreibung des Quiz-Inhalts",
            "questions": [
                {{
                    "question_title": "Frage 1",
                    "question_options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A"
                }},
                // ... weitere 9 Fragen
            ]
        }}

        Regeln:
        - Genau 10 Fragen
        - Jede Frage hat genau 4 Antwortoptionen
        - Die richtige Antwort muss eine der 4 Optionen sein
        - Fragen sollen den Inhalt des Videos testen
        - Verwende klare und verständliche deutsche Sprache
        - Antworte nur mit dem JSON, ohne zusätzlichen Text
        """
        
        response = model.generate_content(prompt)
        quiz_json = response.text
        
        # Clean up response text
        quiz_json = quiz_json.strip()
        if quiz_json.startswith('```json'):
            quiz_json = quiz_json[7:]
        if quiz_json.endswith('```'):
            quiz_json = quiz_json[:-3]
        quiz_json = quiz_json.strip()
        
        # Parse JSON
        quiz_data = json.loads(quiz_json)
        
        # Validate structure
        if not isinstance(quiz_data.get('questions'), list):
            raise ValueError("Invalid quiz structure: questions must be a list")
            
        if len(quiz_data['questions']) != 10:
            raise ValueError("Quiz must have exactly 10 questions")
            
        for i, question in enumerate(quiz_data['questions']):
            if not isinstance(question.get('question_options'), list):
                raise ValueError(f"Question {i+1}: options must be a list")
            if len(question['question_options']) != 4:
                raise ValueError(f"Question {i+1}: must have exactly 4 options")
            if question['answer'] not in question['question_options']:
                raise ValueError(f"Question {i+1}: answer must be one of the options")
        
        return quiz_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")


def cleanup_temp_file(file_path):
    """
    Clean up temporary files.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            # Also remove parent directory if it's a temp directory
            parent_dir = os.path.dirname(file_path)
            if parent_dir.startswith(tempfile.gettempdir()):
                import shutil
                shutil.rmtree(parent_dir, ignore_errors=True)
    except Exception:
        pass  # Ignore cleanup errors


def get_video_info(url):
    """
    Get video information from YouTube URL.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
            }
    except Exception:
        return {
            'title': '',
            'description': '',
            'duration': 0,
            'thumbnail': '',
        }
