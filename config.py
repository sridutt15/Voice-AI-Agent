# config.py
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Load API Keys from environment as fallbacks
MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Log warnings if keys are missing on server startup
if not ASSEMBLYAI_API_KEY:
    logging.warning("ASSEMBLYAI_API_KEY not found in .env. Will rely on client-provided key.")
if not GEMINI_API_KEY:
    logging.warning("GEMINI_API_KEY not found in .env. Will rely on client-provided key.")
if not MURF_API_KEY:
    logging.warning("MURF_API_KEY not found in .env. Will rely on client-provided key.")
if not SERPAPI_API_KEY:
    logging.warning("SERPAPI_API_KEY not found in .env. Web search will be disabled unless client provides a key.")