import os
import subprocess
from config import AUDIO_DIR, OUTPUT_DIR, AUDIO_TO_TEXT_PROVIDER, MAX_MB

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    return round(size_bytes / (1024 * 1024), 2)

def split_audio_if_needed(audio_file_path, max_mb=5):
    """
    Splits the audio file into parts of <= max_mb size using ffmpeg, preserving the original format (e.g., .m4a).
    Saves split files in a subdirectory named after the original file (without extension).
    Returns a list of (part_path, part_index) tuples. If no split is needed, returns the original file.
    """
    size_mb = get_file_size(audio_file_path)
    if size_mb <= max_mb:
        # No splitting needed, do not create any split_dir
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



import difflib
import json

def transcribe_audio(audio_filename, language=None, prompt=None, num_speakers=2):
    """
    Transcribe the audio file, splitting if needed. Uses the provider configured in config.py.
    """
    try:
        from providers import get_audio_to_text_provider
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        base_name = os.path.splitext(os.path.basename(audio_filename))[0]
        split_dir = os.path.join(AUDIO_DIR, base_name)  # For temp split files
        output_dir = os.path.join(OUTPUT_DIR, base_name)
        # Only create split_dir if splitting is needed (handled inside split_audio_if_needed)
        os.makedirs(output_dir, exist_ok=True)

        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file '{audio_file_path}' not found in '{AUDIO_DIR}'!")
            return

        # Split audio if needed (will save in split_dir)
        audio_parts = split_audio_if_needed(audio_file_path, max_mb=MAX_MB)
        multiple_parts = len(audio_parts) > 1

        provider = get_audio_to_text_provider()
        print(f"[INFO] Using provider: {AUDIO_TO_TEXT_PROVIDER}")

        for idx, (part_path, part_idx) in enumerate(audio_parts, 1):
            print(f"Processing part {idx}: {part_path} ({get_file_size(part_path)} MB)")

            try:
                # Request transcription with speaker diarization (local speaker labeling only)
                transcription_text = provider.transcribe(part_path, language=language, prompt=prompt, num_speakers=num_speakers, return_segments=False)
                transcription_path = os.path.join(output_dir, f"{base_name}_part{part_idx}.txt")
                with open(transcription_path, "w", encoding="utf-8") as f:
                    f.write(transcription_text)
                print(f"Saved to '{transcription_path}' ({get_file_size(transcription_path)} MB)")
            except Exception as e:
                print(f"Error transcribing part {idx}: {str(e)}")
            finally:
                if multiple_parts and os.path.exists(part_path):
                    os.remove(part_path)
        # Clean up: remove split_dir if it exists and is empty (avoid leaving empty folders)
        if multiple_parts and os.path.isdir(split_dir) and not os.listdir(split_dir):
            try:
                os.rmdir(split_dir)
            except Exception:
                pass

    except Exception as e:
        print(f"General error: {str(e)}")


def main():
    import argparse
    try:
        from config import DEFAULT_LANGUAGE
        default_language = DEFAULT_LANGUAGE
    except (ImportError, AttributeError):
        default_language = 'en'
    parser = argparse.ArgumentParser(description="Transcribe audio files using the configured provider.")
    parser.add_argument("audio_filename", type=str, help="Audio file location.")
    parser.add_argument("--language", type=str, default=default_language, help="Language code (default: %(default)s)")
    parser.add_argument("--prompt", type=str, default=None, help="Optional custom prompt for transcription.")
    # Only show --num-speakers if ElevenLabs is selected
    try:
        from config import AUDIO_TO_TEXT_PROVIDER
        provider = AUDIO_TO_TEXT_PROVIDER
    except (ImportError, AttributeError):
        provider = 'whisper'
    if provider == "elevenlabs_scribe":
        parser.add_argument("--num-speakers", type=int, default=2, help="Number of speakers for diarization (default: 2, ElevenLabs only)")
    else:
        parser.set_defaults(num_speakers=2)

    args = parser.parse_args()

    transcribe_audio(args.audio_filename, language=args.language, prompt=args.prompt, num_speakers=getattr(args, 'num_speakers', 2))

if __name__ == "__main__":
    main()
