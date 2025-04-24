#Import the openai Library
from openai import OpenAI
import os
import sys
from openai import OpenAIError

def get_file_size(file_path):
    """Get file size in MB"""
    size_bytes = os.path.getsize(file_path)
    return round(size_bytes / (1024 * 1024), 2)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Create an api client using the API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define directories
AUDIO_DIR = "audios"
OUTPUT_DIR = "outputs"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set audio file name (change as needed)
audio_filename = "AUDIO_FILE_PLACEHOLDER.m4a"
audio_file_path = os.path.join(AUDIO_DIR, audio_filename)

# Check if audio file exists
if not os.path.exists(audio_file_path):
    print(f"Error: Audio file '{audio_file_path}' not found in '{AUDIO_DIR}'!")
    sys.exit(1)

# Set output transcription file path
transcription_filename = os.path.splitext(audio_filename)[0] + ".txt"
transcription_path = os.path.join(OUTPUT_DIR, transcription_filename)

# Check if transcription already exists
if os.path.exists(transcription_path):
    print(f"Warning: A transcription file '{transcription_path}' already exists!")
    print(f"Current transcription size: {get_file_size(transcription_path)} MB")
    response = input("Do you want to overwrite it? (yes/no): ")
    if response.lower() != 'yes':
        print("Operation cancelled.")
        sys.exit(0)

# Show audio file size
print(f"Audio file size: {get_file_size(audio_file_path)} MB")
print("Starting transcription process...")

try:
    # Load audio file
    print("Loading audio file...")
    audio_file = open(audio_file_path, "rb")

    # Transcribe with additional parameters
    print("Sending audio to OpenAI for transcription (this may take several minutes)...")
    # transcription = client.audio.transcriptions.create(
    #     model="whisper-1",
    #     file=audio_file,
    #     language="es",  # Specify English language
    #     response_format="text",  # Get plain text output
    #     temperature=0.2,  # Lower temperature for more focused output
    #     prompt="Se trata de una grabación de audio en español con dos interlocutores (entrevistador y entrevistado). Por favor, transcríbala de forma clara y concisa. Identifica el entrevistador y el entrevistado y pon marca de tiempo agrupando por minutos."
    # )
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en",  # Specify English language
        response_format="text",  # Get plain text output
        temperature=0.2,  # Lower temperature for more focused output
        prompt="This is an audio recording in English with two interlocutors (Mentor and mentee). Please transcribe it clearly and concisely. Identify the the both actors clarifiying who said what and put time stamp grouped by minutes."
    )

    # Get the transcription text, handling both string and object responses
    if isinstance(transcription, str):
        transcription_text = transcription
    elif hasattr(transcription, 'text'):
        transcription_text = transcription.text
    else:
        print("Error: Unexpected response format from API")
        print("Response type:", type(transcription))
        print("Response content:", transcription)
        sys.exit(1)

    print("Transcription received, saving to file...")
    print(f"Transcription text length: {len(transcription_text)} characters")

    # Save the transcription to a file
    with open(transcription_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)

    # Print confirmation
    print(f"Transcription has been saved to '{transcription_path}'")
    print(f"Transcription size: {get_file_size(transcription_path)} MB")

except OpenAIError as e:
    print("OpenAI API Error:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response body: {e.response.text}")
    if os.path.exists(transcription_path):
        try:
            os.remove(transcription_path)
            print("Removed incomplete transcription file")
        except:
            print("Warning: Could not remove incomplete transcription file")
    sys.exit(1)
except Exception as e:
    print("Unexpected error:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    if os.path.exists(transcription_path):
        try:
            os.remove(transcription_path)
            print("Removed incomplete transcription file")
        except:
            print("Warning: Could not remove incomplete transcription file")
    sys.exit(1)