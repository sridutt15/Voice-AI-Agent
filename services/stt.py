# services/stt.py
from assemblyai.streaming.v3 import StreamingClient, StreamingClientOptions, StreamingParameters, StreamingEvents, TurnEvent, StreamingError
import logging

class AssemblyAIStreamingTranscriber:
    def __init__(self, api_key: str, sample_rate: int = 16000, on_final_callback=None):
        if not api_key:
            raise ValueError("AssemblyAI API key is required.")
        self.on_final_callback = on_final_callback
        self.client = StreamingClient(StreamingClientOptions(api_key=api_key))
        self.client.on(StreamingEvents.Error, self._on_error)
        self.client.on(StreamingEvents.Turn, self._on_turn)
        self.client.connect(StreamingParameters(sample_rate=sample_rate))

    def _on_error(self, client: StreamingClient, error: StreamingError):
        logging.error(f"AssemblyAI streaming error: {error}")

    def _on_turn(self, client: StreamingClient, event: TurnEvent):
        text = (event.transcript or "").strip()
        if not text:
            return
        if event.end_of_turn and self.on_final_callback:
            self.on_final_callback(text)

    def stream_audio(self, audio_chunk: bytes):
        self.client.stream(audio_chunk)

    def close(self):
        self.client.disconnect(terminate=True)