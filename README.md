# Whisper Transcriber

A powerful and extensible CLI tool to transcribe audio files using either the OpenAI Whisper API or ElevenLabs Scribe API. 

Features include:
- Support for multiple audio-to-text providers (Whisper and ElevenLabs Scribe), configurable in `config.py`.
- Automatic splitting of large audio files for seamless transcription, using ffmpeg.
- Speaker diarization (speaker identification and separation) when using ElevenLabs Scribe, with configurable number of speakers.
- Customizable transcription prompts and parameters per provider and per language.
- Outputs transcriptions and speaker mapping files for reproducibility.
- All settings, API keys, and parameters are managed in `config.py` for easy customization.
- Designed to be easily extended with new providers.


## Project Structure

```
whisper-transcriber/
├── transcribe.py     # Main transcription script
├── config.py         # Project configuration
├── providers.py      # Provider management
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

### Using ElevenLabs Scribe

To use the ElevenLabs Scribe provider for transcription with speaker diarization:

1. Set `AUDIO_TO_TEXT_PROVIDER = "elevenlabs_scribe"` in your `config.py`.
2. Add your ElevenLabs API key to your `.env` file:
   ```
   ELEVENLABS_API_KEY=your-elevenlabs-api-key
   ```
3. Place your audio files in the `audios/` folder.
4. Run the transcription command:
   ```bash
   python3 transcribe.py audios/your_audio_file.m4a --language es --num-speakers 2
   ```
   - The `--num-speakers` argument is optional and controls the number of speakers for diarization.
   - The output will include speaker labels as `speaker_1`, `speaker_2`, etc., local to each audio part.

The ElevenLabs Scribe provider supports automatic splitting of large audio files and generates clear diarized transcripts per fragment.

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
