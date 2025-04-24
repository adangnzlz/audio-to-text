from openai import OpenAI, OpenAIError
import os
import sys
from config import (
    AUDIO_DIR, OUTPUT_DIR, OPENAI_API_KEY, DEFAULT_LANGUAGE, DEFAULT_PROMPT,
    DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_RESPONSE_FORMAT
)

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    return round(size_bytes / (1024 * 1024), 2)


def transcribe_audio(audio_filename, language=DEFAULT_LANGUAGE, prompt=None):
    client = OpenAI(api_key=OPENAI_API_KEY)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
    transcription_filename = os.path.splitext(audio_filename)[0] + ".txt"
    transcription_path = os.path.join(OUTPUT_DIR, transcription_filename)

    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file '{audio_file_path}' not found in '{AUDIO_DIR}'!")
        sys.exit(1)

    if os.path.exists(transcription_path):
        print(f"Warning: A transcription file '{transcription_path}' already exists!")
        print(f"Current transcription size: {get_file_size(transcription_path)} MB")
        response = input("Do you want to overwrite it? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            sys.exit(0)

    print(f"Audio file size: {get_file_size(audio_file_path)} MB")
    print("Starting transcription process...")

    try:
        print("Loading audio file...")
        with open(audio_file_path, "rb") as audio_file:
            print("Sending audio to OpenAI for transcription (this may take several minutes)...")
            transcription = client.audio.transcriptions.create(
                model=DEFAULT_MODEL,
                file=audio_file,
                language=language,
                response_format=DEFAULT_RESPONSE_FORMAT,
                temperature=DEFAULT_TEMPERATURE,
                prompt=prompt or DEFAULT_PROMPT.get(language, "")
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
        with open(transcription_path, "w", encoding="utf-8") as f:
            f.write(transcription_text)
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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Transcribe an audio file using OpenAI Whisper API.")
    parser.add_argument("audio_filename", help="Name of the audio file in the 'audios' directory")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, choices=["en","es"], help="Language of the transcription")
    parser.add_argument("--prompt", default=None, help="Custom prompt for transcription")
    args = parser.parse_args()
    transcribe_audio(args.audio_filename, language=args.language, prompt=args.prompt)

if __name__ == "__main__":
    main()
