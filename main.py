# main.py
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import asyncio
import base64
import re
from websockets.exceptions import ConnectionClosed

# Import services and config
import config
from services import stt, llm, tts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    assemblyai_key: str = Query(None),
    gemini_key: str = Query(None),
    murf_key: str = Query(None),
    serpapi_key: str = Query(None),
):
    """Handles WebSocket connection for real-time transcription and voice response."""
    await websocket.accept()
    logging.info("WebSocket client connected.")

    # 1. Resolve API Keys: Use client-provided keys or fall back to .env
    final_aai_key = assemblyai_key or config.ASSEMBLYAI_API_KEY
    final_gemini_key = gemini_key or config.GEMINI_API_KEY
    final_murf_key = murf_key or config.MURF_API_KEY
    final_serpapi_key = serpapi_key or config.SERPAPI_API_KEY

    # Check if essential keys are missing
    if not all([final_aai_key, final_gemini_key, final_murf_key]):
        logging.error("Missing one or more essential API keys.")
        await websocket.send_json({"type": "error", "message": "Server is missing essential API keys."})
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    chat_history = []

    async def handle_transcript(text: str):
        """Processes final transcript, gets LLM/TTS responses, and streams audio."""
        await websocket.send_json({"type": "final", "text": text})

        try:
            # Decide if a web search is needed
            should_search = llm.should_search_web(text, final_gemini_key)

            if should_search and final_serpapi_key:
                full_response, updated_history = llm.get_web_response(text, chat_history, final_gemini_key, final_serpapi_key)
            else:
                full_response, updated_history = llm.get_llm_response(text, chat_history, final_gemini_key)

            # Update history for the next turn
            chat_history.clear()
            chat_history.extend(updated_history)

            await websocket.send_json({"type": "assistant", "text": full_response})

            # Split response into sentences for smoother TTS streaming
            sentences = re.split(r'(?<=[.?!])\s+', full_response.strip())
            
            for sentence in sentences:
                clean_sentence = sentence.strip()
                if clean_sentence:
                    # Run the blocking TTS function in a separate thread
                    audio_bytes = await loop.run_in_executor(
                        None, tts.speak, clean_sentence, final_murf_key
                    )
                    if audio_bytes:
                        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        await websocket.send_json({"type": "audio", "b64": b64_audio})

        except (WebSocketDisconnect, ConnectionClosed) as e:
            logging.warning(f"Client disconnected during processing: {e}")
        except Exception as e:
            logging.error(f"Error in LLM/TTS pipeline: {e}", exc_info=True)
            await websocket.send_json({"type": "assistant", "text": "Sorry, I encountered an error."})


    def on_final_transcript(text: str):
        """Callback to safely schedule the async handler from the transcriber thread."""
        logging.info(f"Final transcript received: {text}")
        asyncio.run_coroutine_threadsafe(handle_transcript(text), loop)

    # Initialize transcriber with the resolved API key
    transcriber = stt.AssemblyAIStreamingTranscriber(
        api_key=final_aai_key,
        on_final_callback=on_final_transcript
    )

    try:
        while True:
            data = await websocket.receive_bytes()
            transcriber.stream_audio(data)
    except WebSocketDisconnect:
        logging.info("WebSocket client disconnected.")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        transcriber.close()
        logging.info("Transcription resources released.")