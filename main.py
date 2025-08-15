from fastapi import FastAPI, Request, UploadFile, File, Path
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests
import os
import assemblyai as aai
import google.generativeai as genai
from typing import Dict, List, Any

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# --- SETUP DIRECTORIES ---
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("templates"):
    os.makedirs("templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- LOAD API KEYS ---
MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- CONFIGURE APIS ---
if ASSEMBLYAI_API_KEY:
    aai.settings.api_key = ASSEMBLYAI_API_KEY
else:
    print("Warning: ASSEMBLYAI_API_KEY not found.")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found.")

chat_histories: Dict[str, List[Dict[str, Any]]] = {}

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/agent/chat/{session_id}")
async def agent_chat(
    session_id: str = Path(..., description="The unique ID for the chat session."),
    audio_file: UploadFile = File(...)
):
    fallback_audio_path = "static/fallback.mp3"

    if not all([GEMINI_API_KEY, ASSEMBLYAI_API_KEY, MURF_API_KEY]):
        print("An API key is missing. Returning fallback audio.")
        return FileResponse(fallback_audio_path, media_type="audio/mpeg", headers={"X-Error": "true"})

    try:
        # 1. Transcribe audio to text
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file.file)

        if transcript.status == aai.TranscriptStatus.error or not transcript.text:
            raise Exception(f"Transcription failed: {transcript.error or 'No speech detected'}")

        user_query_text = transcript.text
      
        # 2. Get LLM response
        session_history = chat_histories.get(session_id, [])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        chat = model.start_chat(history=session_history)
        response = chat.send_message(user_query_text)
        llm_response_text = response.text

        # 3. Update history
        chat_histories[session_id] = chat.history

        # 4. Generate TTS
        url = "https://api.murf.ai/v1/speech/generate"
        headers = {"Content-Type": "application/json", "api-key": MURF_API_KEY}
        payload = {"text": llm_response_text, "voiceId": "en-US-natalie", "format": "MP3"}

        murf_response = requests.post(url, json=payload, headers=headers)
        murf_response.raise_for_status()
        audio_url = murf_response.json().get("audioFile")

        if audio_url:
            # MODIFIED: Return user and agent text along with the audio URL
            return JSONResponse(content={
                "audio_url": audio_url,
                "user_text": user_query_text,
                "agent_text": llm_response_text
            })
        else:
            raise Exception("Murf API did not return an audio file.")

    except Exception as e:
        print(f"An error occurred in the agent chat endpoint: {e}")
        return FileResponse(fallback_audio_path, media_type="audio/mpeg", headers={"X-Error": "true"})