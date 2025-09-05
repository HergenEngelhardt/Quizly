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


def extract_youtube_id(url):
    """
    Extract YouTube video ID from URL.
    """
    parsed_url = urlparse(url)

    if parsed_url.hostname in ["youtu.be"]:
        return parsed_url.path[1:]
    elif parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query)["v"][0]
        elif parsed_url.path.startswith("/embed/"):
            return parsed_url.path.split("/")[2]
        elif parsed_url.path.startswith("/v/"):
            return parsed_url.path.split("/")[2]

    return None


def create_ydl_options(output_file):
    """
    Create yt-dlp options configuration.
    """
    return {
        "format": "bestaudio/best",
        "outtmpl": output_file,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }


def extract_audio_file(url, ydl_opts):
    """
    Extract audio using yt-dlp.
    """
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def verify_audio_file(temp_dir):
    """
    Verify audio file exists and return path.
    """
    audio_file = os.path.join(temp_dir, "audio.wav")
    if os.path.exists(audio_file):
        return audio_file
    else:
        raise Exception("Audio file not found after download")


def download_youtube_audio(url):
    """
    Download YouTube video as audio file.
    """
    try:
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "audio.%(ext)s")

        ydl_opts = create_ydl_options(output_file)
        extract_audio_file(url, ydl_opts)

        return verify_audio_file(temp_dir)

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


def configure_gemini_model():
    """
    Configure and return Gemini AI model.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")


def get_quiz_structure_template():
    """
    Get the basic quiz structure template.
    """
    return '''{{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }},
    ...
    (exactly 10 questions)
  ]
}}'''


def get_quiz_requirements():
    """
    Get the requirements text for quiz generation.
    """
    return '''Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.'''


def create_quiz_prompt(transcript, video_title):
    """
    Create prompt for Gemini AI.
    """
    structure = get_quiz_structure_template()
    requirements = get_quiz_requirements()
    
    return f"""Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{structure}

{requirements}

{transcript}"""


def parse_quiz_response(response_text):
    """
    Parse and clean Gemini AI response.
    """
    quiz_json = response_text.strip()
    if quiz_json.startswith("```json"):
        quiz_json = quiz_json[7:]
    if quiz_json.endswith("```"):
        quiz_json = quiz_json[:-3]
    return quiz_json.strip()


def validate_quiz_structure(quiz_data):
    """
    Validate quiz data structure.
    """
    if not isinstance(quiz_data.get("questions"), list):
        raise ValueError("Invalid quiz structure: questions must be a list")

    if len(quiz_data["questions"]) != 10:
        raise ValueError("Quiz must have exactly 10 questions")

    for i, question in enumerate(quiz_data["questions"]):
        if not isinstance(question.get("question_options"), list):
            raise ValueError(f"Question {i+1}: options must be a list")
        if len(question["question_options"]) != 4:
            raise ValueError(f"Question {i+1}: must have exactly 4 options")
        if question["answer"] not in question["question_options"]:
            raise ValueError(f"Question {i+1}: answer must be one of the options")


def generate_quiz_from_transcript(transcript, video_title=""):
    """
    Generate quiz from transcript using Gemini AI.
    """
    try:
        model = configure_gemini_model()
        prompt = create_quiz_prompt(transcript, video_title)

        response = model.generate_content(prompt)
        quiz_json = parse_quiz_response(response.text)

        quiz_data = json.loads(quiz_json)
        validate_quiz_structure(quiz_data)

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
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", ""),
            }
    except Exception:
        return {
            "title": "",
            "description": "",
            "duration": 0,
            "thumbnail": "",
        }
