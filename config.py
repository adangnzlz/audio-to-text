from dotenv import load_dotenv
import os

load_dotenv()

# General paths
AUDIO_DIR = "./"
OUTPUT_DIR = "./outputs"

# Maximum audio file size for splitting (in MB). Do not set above 7 MB.
MAX_MB = 7  # Max allowed

# Provider selection for audio-to-text
AUDIO_TO_TEXT_PROVIDER = "elevenlabs_scribe"  # Options: "whisper", "elevenlabs_scribe"

# Per-provider configuration dictionary
AUDIO_TO_TEXT_PROVIDERS = {
    "whisper": {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "DEFAULT_MODEL": "whisper-1",
        "DEFAULT_LANGUAGE": "en",
        "DEFAULT_PROMPT": {
            "en": "This is an audio recording in English with two interlocutors (Mentor and mentee). Please transcribe it clearly and concisely. Identify both actors clarifying who said what and put time stamp grouped by minutes.",
            "es": "Se trata de una grabación de audio en español con dos interlocutores (entrevistador y entrevistado). Por favor, transcríbala de forma clara y concisa. Identifica el entrevistador y el entrevistado y pon marca de tiempo agrupando por minutos."
        },
        "DEFAULT_TEMPERATURE": 0.2,
        "DEFAULT_RESPONSE_FORMAT": "text",
    },
    "elevenlabs_scribe": {
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
        # Add more ElevenLabs-specific parameters here if needed
        # Example: "DEFAULT_LANGUAGE": "en",
    },
}

