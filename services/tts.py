# services/tts.py
import logging
from murf import Murf

logger = logging.getLogger(__name__)

def speak(text: str, murf_api_key: str) -> bytes:
    """Convert text to speech using Murf API and return the audio as bytes."""
    if not murf_api_key:
        logger.error("MURF_API_KEY was not provided for the TTS request.")
        return b""
    
    try:
        client = Murf(api_key=murf_api_key)
        res = client.text_to_speech.stream(
            text=text,
            voice_id="en-US-ken",
            style="Conversational"
        )
        audio_bytes = b"".join(res)
        return audio_bytes
    except Exception as e:
        logger.error(f"Error during Murf TTS request: {e}")
        return b""