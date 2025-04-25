from openai import OpenAI, OpenAIError
import os
import sys
from config import (
    AUDIO_DIR, OUTPUT_DIR, OPENAI_API_KEY, DEFAULT_LANGUAGE, DEFAULT_PROMPT,
    DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_RESPONSE_FORMAT
)
from pydub import AudioSegment
import math

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    return round(size_bytes / (1024 * 1024), 2)


import subprocess

def split_audio_if_needed(audio_file_path, max_mb=5):
    """
    Splits the audio file into parts of <= max_mb size using ffmpeg, preserving the original format (e.g., .m4a).
    Saves split files in a subdirectory named after the original file (without extension).
    Returns a list of (part_path, part_index) tuples. If no split is needed, returns the original file.
    """
    size_mb = get_file_size(audio_file_path)
    if size_mb <= max_mb:
        return [(audio_file_path, 1)]

    print(f"Audio file is {size_mb} MB, splitting into parts of <= {max_mb} MB...")

    # Get duration in seconds using ffprobe
    import json
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'json', audio_file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration_sec = float(json.loads(result.stdout)['format']['duration'])

    # Calculate bytes per second
    size_bytes = os.path.getsize(audio_file_path)
    bytes_per_sec = size_bytes / duration_sec
    max_bytes = max_mb * 1024 * 1024
    max_sec = int(max_bytes / bytes_per_sec)
    num_parts = int(duration_sec // max_sec) + (1 if duration_sec % max_sec else 0)

    ext = os.path.splitext(audio_file_path)[1].lstrip('.')
    base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    split_dir = os.path.join(os.path.dirname(audio_file_path), base_name)
    os.makedirs(split_dir, exist_ok=True)
    part_paths = []

    for i in range(num_parts):
        start = i * max_sec
        part_path = os.path.join(split_dir, f"{base_name}_part{i+1}.{ext}")
        # Use ffmpeg to split without re-encoding
        split_cmd = [
            'ffmpeg', '-y', '-i', audio_file_path, '-ss', str(start), '-t', str(max_sec),
            '-c', 'copy', part_path
        ]
        subprocess.run(split_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        part_paths.append((part_path, i + 1))
    return part_paths



def transcribe_audio(audio_filename, language=DEFAULT_LANGUAGE, prompt=None):
    """ Transcribe the audio file, splitting if needed. """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        base_name = os.path.splitext(os.path.basename(audio_filename))[0]
        # Create subdirectories for split audio and output
        split_dir = os.path.join(AUDIO_DIR, base_name)
        output_dir = os.path.join(OUTPUT_DIR, base_name)
        os.makedirs(split_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file '{audio_file_path}' not found in '{AUDIO_DIR}'!")
            return

        # Split audio if needed (will save in split_dir)
        audio_parts = split_audio_if_needed(audio_file_path, max_mb=5)
        multiple_parts = len(audio_parts) > 1

        for part_path, idx in audio_parts:
            if multiple_parts:
                transcription_filename = f"{base_name}_part{idx}.txt"
            else:
                transcription_filename = f"{base_name}.txt"
            transcription_path = os.path.join(output_dir, transcription_filename)

            if os.path.exists(transcription_path):
                print(f"Warning: '{transcription_path}' exists! Overwrite? (yes/no): ", end="")
                response = input()
                if response.lower() != 'yes':
                    print("Skipped.")
                    if multiple_parts:
                        os.remove(part_path)
                    continue

            print(f"Processing part {idx}: {part_path} ({get_file_size(part_path)} MB)")

            try:
                with open(part_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model=DEFAULT_MODEL,
                        file=audio_file,
                        language=language,
                        response_format=DEFAULT_RESPONSE_FORMAT,
                        temperature=DEFAULT_TEMPERATURE,
                        prompt=prompt or DEFAULT_PROMPT.get(language, "")
                    )

                transcription_text = getattr(transcription, 'text', transcription) if not isinstance(transcription, str) else transcription
                with open(transcription_path, "w", encoding="utf-8") as f:
                    f.write(transcription_text)
                print(f"Saved to '{transcription_path}' ({get_file_size(transcription_path)} MB)")
            except Exception as e:
                print(f"Error transcribing part {idx}: {str(e)}")
            finally:
                if multiple_parts:
                    os.remove(part_path)
    except Exception as e:
        print(f"General error: {str(e)}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI Whisper API.")
    parser.add_argument("audio_filename", type=str, help="Audio file location.")
    parser.add_argument("--language", type=str, default=DEFAULT_LANGUAGE, help="Language code (default: %(default)s)")
    parser.add_argument("--prompt", type=str, default=None, help="Optional custom prompt for transcription.")

    args = parser.parse_args()

    transcribe_audio(args.audio_filename, language=args.language, prompt=args.prompt)


if __name__ == "__main__":
    main()
