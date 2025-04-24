# Whisper Transcriber

A simple CLI tool to transcribe audio files using the OpenAI Whisper API.

## Project Structure

```
whisper-transcriber/
├── transcribe.py     # Main transcription script
├── config.py         # Project configuration
├── audios/           # Folder for audio files (not tracked by git)
├── outputs/          # Folder for transcription outputs (not tracked by git)
├── .env              # Environment variables (your API KEY here, not tracked by git)
├── .gitignore
├── README.md
└── ...
```

## Installation

1. Clone the repository and enter the folder.
2. Install the required dependencies:

```bash
pip install openai python-dotenv
```

3. Create a `.env` file in the root with your OpenAI API key:

```
OPENAI_API_KEY=sk-...your-api-key...
```

4. Place your audio files in the `audios/` folder.

## Usage

From the root of the project:

```bash
python transcribe.py <audio_filename> [--language en|es] [--prompt "Optional custom prompt text"]
```

- `<audio_filename>`: The name of the audio file inside the `audios/` folder (e.g. `my_audio.m4a`)
- `--language`: Transcription language (`en` for English, `es` for Spanish). Default is English.
- `--prompt`: (Optional) Custom prompt for the transcription.

Example:

```bash
python transcribe.py my_audio.m4a --language es
```

The transcription will be automatically saved in the `outputs/` folder with the same base name and `.txt` extension.

## Notes
- Do not commit your `.env` file or the `audios/` and `outputs/` folders to git (they are already in `.gitignore`).
- You can modify the default prompts or parameters in `config.py`.

---

**Comments welcome!**
