# 🎙 Voice AI Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/) 
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/) 
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript) 
[![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red.svg)](#) 

## Overview 📝

*This repository contains the code for a fully interactive, **Voice-Activated AI agent** built with FastAPI and modern web technologies. The project documents the journey of creating a sophisticated conversational AI from scratch. The final application allows a user to have a natural, voice-to-voice conversation with an AI that can remember the context of the dialogue, all powered by a robust stack of AI services.*
 
## Key Features ✨

* ****End-to-End Voice Conversation****: *A seamless, voice-in, voice-out interaction loop.*

* ****Session-Based Memory****: *The agent remembers the context of the conversation within a session, allowing for natural follow-up questions.*

* ****Real-time Visual Feedback****: *The UI dynamically updates to show whether the agent is idle, recording, or processing, providing a clear user experience.*

* ****Transcript Display****: *An optional, toggleable transcript allows users to see the conversation in text form.*

* ****Graceful Error Handling****: *A fallback audio response is played if any backend process fails, preventing a jarring user experience.*

* ****Secure API Key Management****: *All API keys are loaded from a `.env` file and are never exposed on the client-side.*

## TechStack & Purpose 🛠️

*This project integrates several technologies to create a cohesive experience.*

### Frontend (Browser)

* ****HTML, CSS, & JavaScript****: *The core technologies for building the user interface and client-side logic.*

* ****Bootstrap****: *A CSS framework used for UI components like the loading spinner.*

* ****MediaRecorder API****: *A browser-based API used to capture audio directly from the user's microphone.*

### Backend (Python)

* ****FastAPI****: *A high-performance web framework used to build the API that connects the frontend to the AI services.*

* ****Uvicorn****: *The ASGI server that runs the FastAPI application.*

* ****Python-Dotenv****: *Manages environment variables, allowing for secure handling of API keys by loading them from a `.env` file.*

* ****Requests****: *A simple and powerful library for making HTTP requests to the Murf AI API.*

* ****AssemblyAI SDK****: *The official Python client for AssemblyAI's Speech-to-Text API.*

* ****Google Generative AI SDK****: *The official Python client for the Google Gemini Large Language Model.*

## Architecture 🏗️

The application follows a ****Client-Server Architecture****.

* ****Client (Frontend)****: *The user interface running in the browser. It is responsible for capturing user audio and displaying the agent's response.*

* ****Server (Backend)****: The FastAPI application acts as an orchestrator. It receives audio from the client and manages the entire AI pipeline by communicating with the various external APIs (AssemblyAI, Gemini, Murf AI) in sequence.

## How It Works ⚙️

Here is the step-by-step flow for a single turn in a conversation:

1. ****Audio Capture****: The user clicks the record button, and the browser's `MediaRecorder` API captures their voice.

2. ****Send to Server****: The captured audio is sent as a file to the FastAPI backend.

3. ****Speech-to-Text (STT)****: The server forwards the audio to **AssemblyAI**, which transcribes it into text.

4. ****LLM Processing****: The transcribed text is sent to the **Google Gemini** model along with the previous conversation history for that session.

5. ****Generate Response****: Gemini generates a contextually relevant text response.

6. ****Update History****: The server updates the session's chat history with the new user query and agent response.

7. ****Text-to-Speech (TTS)****: The agent's text response is sent to the **Murf AI** API to be converted into high-quality audio.

8. ****Respond to Client****: The server sends a JSON object containing the URL of the generated audio and the text transcript back to the client.

9. ****Playback****: The browser plays the audio response, updates the transcript on the screen, and the UI returns to an idle state, ready for the next interaction.

## Getting Started 🚀

Follow these instructions to get a local copy up and running.

### Prerequisites

* Python 3.8+

* API keys for:

  * Murf AI

  * AssemblyAI

  * Google Gemini

### Installation & Setup

1. ****Clone the repository:****

   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
   ```

2. ****Install Python dependencies:****

   ```bash
   pip install -r requirements.txt
   ```

3. ****Create an environment file:****
   Create a file named `.env` in the root of the project directory and add your API keys:

   ```
   MURF_API_KEY="your_murf_api_key_here"
   ASSEMBLYAI_API_KEY="your_assemblyai_api_key_here"
   GEMINI_API_KEY="your_gemini_api_key_here"
   ```

4. ****Run the server:****

   ```bash
   uvicorn main:app --reload
   ```

5. ****Open the application:****
   Navigate to `http://127.0.0.1:8000` in your web browser. Grant microphone permissions when prompted and start talking!

## ⚠️ Important Notes

* ****API Key Security****: Your `.env` file contains sensitive API keys. **Do not** commit this file to GitHub or share it publicly. Ensure that `.env` is listed in your `.gitignore` file.

* ****In-Memory Chat History****: The conversation history is stored in a Python dictionary on the server. This means that **all chat histories will be erased if the server restarts**. For persistent storage, you would need to integrate a database.


<!-- [![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)-->
<!-- [![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red.svg)](#)-->