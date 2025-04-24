from dotenv import load_dotenv
import os

load_dotenv()

AUDIO_DIR = "audios"
OUTPUT_DIR = "outputs"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Default parameters for transcription
DEFAULT_LANGUAGE = "en"
DEFAULT_PROMPT = {
    "en": "This is an audio recording in English with two interlocutors (Mentor and mentee). Please transcribe it clearly and concisely. Identify both actors clarifying who said what and put time stamp grouped by minutes.",
    "es": "Esta es una grabación de audio en Español con dos interlocutores (mentor y aprendiz). Por favor, transcribe el contenido de forma clara y concisa. Identifica a ambos actores aclarando quién dijo qué y agrega marcas de tiempo agrupadas por minutos."
}
DEFAULT_MODEL = "whisper-1"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_RESPONSE_FORMAT = "text"
