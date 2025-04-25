# providers.py
# Provider pattern for audio-to-text conversion
# Comments in English, as per user preference

from abc import ABC, abstractmethod
import difflib  # For fuzzy speaker matching

class AudioToTextProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, language: str = None, prompt: str = None, num_speakers: int = None) -> str:
        """
        Transcribe the given audio file to text using the provider's configuration.
        Args:
            audio_path (str): Path to the audio file.
            language (str, optional): Language code for transcription. Uses provider default if None.
            prompt (str, optional): Prompt for the model. Uses provider default if None.
        Returns:
            str: Transcribed text (empty string on error).
        """
        pass


class WhisperProvider(AudioToTextProvider):
    def transcribe(self, audio_path: str, language: str = None, prompt: str = None) -> str:
        """
        Transcribe using OpenAI Whisper API, using config from AUDIO_TO_TEXT_PROVIDERS.
        """
        from config import AUDIO_TO_TEXT_PROVIDERS
        from openai import OpenAI, OpenAIError
        config = AUDIO_TO_TEXT_PROVIDERS["whisper"]
        client = OpenAI(api_key=config["OPENAI_API_KEY"])
        try:
            with open(audio_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model=config["DEFAULT_MODEL"],
                    file=audio_file,
                    language=language or config["DEFAULT_LANGUAGE"],
                    prompt=prompt or config["DEFAULT_PROMPT"].get(language or config["DEFAULT_LANGUAGE"], ""),
                    response_format=config["DEFAULT_RESPONSE_FORMAT"],
                    temperature=config["DEFAULT_TEMPERATURE"]
                )
            return response.text if hasattr(response, 'text') else response
        except OpenAIError as e:
            print(f"OpenAI Whisper API error: {e}")
            return ""


# ElevenLabs Scribe provider
class ScribeProvider(AudioToTextProvider):
    def transcribe(self, audio_path: str, language: str = None, prompt: str = None, num_speakers: int = 2, return_segments: bool = False, global_speaker_map=None, global_speaker_texts=None, next_speaker_id=1):
        """
        Transcribe using ElevenLabs Scribe API, using config from AUDIO_TO_TEXT_PROVIDERS.
        """
        from config import AUDIO_TO_TEXT_PROVIDERS
        import requests
        config = AUDIO_TO_TEXT_PROVIDERS["elevenlabs_scribe"]
        api_key = config["ELEVENLABS_API_KEY"]
        if not api_key:
            print("ELEVENLABS_API_KEY not set in config.")
            return ""
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        headers = {
            "xi-api-key": api_key
        }
        # Prepare data for ElevenLabs Scribe API
        data = {}
        # Required model_id for ElevenLabs Scribe API. Must be 'scribe_v1' (not 'scribe-1') according to latest docs and error message.
        data["model_id"] = "scribe_v1"
        # Enable speaker diarization
        data["diarize"] = True  # Always enable diarization
        # Optionally set the expected number of speakers
        if num_speakers is not None:
            data["num_speakers"] = num_speakers
        if language:
            # The correct parameter is 'language_code' according to ElevenLabs docs
            data["language_code"] = language
        if prompt:
            data["prompt"] = prompt
        try:
            with open(audio_path, "rb") as audio_fp:
                # The correct field name for the file is 'file', not 'audio'
                files = {"file": audio_fp}
                response = requests.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()
                result = response.json()
                # print("[DEBUG] ElevenLabs Scribe API full response:", result)  # Debug removed
                # If diarization is present, format with per-part speaker mapping
                if "words" in result:
                    output_lines = []
                    current_speaker = None
                    current_line = []
                    local_speaker_first_text = {}
                    local_to_global = {}
                    segments = []
                    # Build local speaker first utterance
                    for word in result["words"]:
                        if word["type"] != "word":
                            continue
                        spk = word.get("speaker_id", "speaker_0")
                        if spk not in local_speaker_first_text:
                            local_speaker_first_text[spk] = word["text"]
                        else:
                            if len(local_speaker_first_text[spk]) < 80:
                                local_speaker_first_text[spk] += " " + word["text"]
                    # Assign speaker numbers as 'speaker_1', 'speaker_2', ... per part (local counter only)
                    speaker_ids = list(local_speaker_first_text.keys())
                    speaker_map = {spk: f"speaker_{i+1}" for i, spk in enumerate(speaker_ids)}
                    # Build output
                    for word in result["words"]:
                        if word["type"] != "word":
                            continue
                        spk = word.get("speaker_id", "speaker_0")
                        speaker_label = speaker_map.get(spk, "speaker_1")
                        if current_speaker != spk:
                            if current_line:
                                output_lines.append(f"{speaker_label}: {' '.join(current_line)}")
                                segments.append((speaker_label, ' '.join(current_line)))
                            current_speaker = spk
                            current_line = [word["text"]]
                        else:
                            current_line.append(word["text"])
                    if current_line:
                        output_lines.append(f"{speaker_map.get(current_speaker, 'speaker_1')}: {' '.join(current_line)}")
                        segments.append((speaker_map.get(current_speaker, 'speaker_1'), ' '.join(current_line)))
                    if return_segments:
                        return "\n".join(output_lines), segments
                    return "\n".join(output_lines)
                # Fallback: plain text
                return result.get("text", "")
        except Exception as e:
            # Print detailed error message from ElevenLabs API if available
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"ElevenLabs Scribe API error: {e}\nResponse content: {e.response.text}")
                except Exception:
                    print(f"ElevenLabs Scribe API error: {e} (could not read response text)")
            else:
                print(f"ElevenLabs Scribe API error: {e}")
            return ""


def get_audio_to_text_provider():
    """
    Factory function to select and instantiate the correct provider based on config.
    """
    from config import AUDIO_TO_TEXT_PROVIDER
    if AUDIO_TO_TEXT_PROVIDER == "whisper":
        return WhisperProvider()
    elif AUDIO_TO_TEXT_PROVIDER == "elevenlabs_scribe":
        return ScribeProvider()
    else:
        raise ValueError(f"Unknown AUDIO_TO_TEXT_PROVIDER: {AUDIO_TO_TEXT_PROVIDER}")