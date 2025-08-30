# 🎙️ My Voice AI Agent with Web Search

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-blueviolet)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red.svg)](#)
## Overview 📝

This repository contains the code for **My Voice Assistant**, a fully interactive, **real-time voice AI agent**. Built with a streaming-first architecture using WebSockets and FastAPI, this project moves beyond simple request-response models to enable fluid, low-latency conversations.

My Assistant can understand you as you speak, think, and talk back in a continuous flow. It remembers the context of your conversation, can **search the web for up-to-the-minute information**, and allows users to securely use their own API keys directly in the browser.



---

## Key Features ✨

* ****⚡ Real-Time Streaming:**** End-to-end audio streaming for both Speech-to-Text (STT) and Text-to-Speech (TTS) using WebSockets, providing a highly responsive and natural conversational experience.

* ****🧠 Live Web Search:**** MARVIS can determine when a query requires current information (e.g., "What's the weather today?") and use ****SerpApi**** to perform a live Google search to provide accurate, timely answers.

* ****👤 Defined AI Persona:**** The agent operates with a pre-defined personality inspired by JARVIS, making interactions more engaging and consistent.

* ****🔑 Client-Side API Key Management:**** A secure settings modal allows users to enter their own API keys, which are stored in the browser's `localStorage` and never exposed to the server logs or other users. The server can also be configured with fallback keys.

* ****💬 Session-Based Memory:**** The agent maintains conversation history within a single WebSocket session, allowing for contextual follow-up questions.

* ****🖥️ Rich Frontend:**** A clean, modern UI built with a glassmorphism design that provides real-time feedback on the agent's status (listening, thinking, speaking) and displays a live transcript of the conversation.

---

## Tech Stack & Purpose 🛠️

This project integrates several key technologies to create its real-time architecture.

### Frontend (Browser)

* ****HTML, CSS, & JavaScript****: The core for the user interface and client-side logic.

* ****WebSockets API****: The backbone of real-time, bidirectional communication between the client and the server.

* ****MediaStream API****: Captures microphone audio, which is then processed and streamed to the backend.

### Backend (Python)

* ****FastAPI****: A high-performance web framework used to handle WebSocket connections and orchestrate the AI services.

* ****Uvicorn****: The ASGI server that runs the FastAPI application.

* ****AssemblyAI SDK****: Used for real-time streaming transcription of the user's voice.

* ****Google Generative AI SDK****: Provides access to the Gemini Large Language Model for generating intelligent responses.

* ****Murf SDK****: Used for streaming Text-to-Speech synthesis to generate the agent's voice in real-time.

* ****Google Search Results (SerpApi)****: The library used to perform live web searches.

* ****Python-Dotenv****: Manages server-side fallback API keys from a `.env` file.

---

## Architecture 🏗️

The application uses a **WebSocket-based streaming architecture** to minimize latency.



* ****Client (Frontend)****: The browser establishes a persistent WebSocket connection to the server. It continuously streams raw microphone audio to the backend and plays incoming audio chunks from the server as they arrive.

* ****Server (Backend)****: The FastAPI server acts as a central hub. It manages the WebSocket connection and orchestrates the flow of data between the various AI services in a non-blocking, asynchronous manner.

---

## How It Works ⚙️

1.  ****WebSocket Connection****: The user opens the web page, and the browser establishes a WebSocket connection with the FastAPI server, passing API keys from `localStorage` as query parameters.

2.  ****Audio Streaming (Client → Server)****: The user holds the record button. The browser captures audio and streams it in small chunks to the 
server over the WebSocket.

3.  ****Real-Time Transcription (Server ↔ AssemblyAI)****: The server forwards the audio chunks to **AssemblyAI's** streaming STT service. Once the user finishes speaking, AssemblyAI returns the final transcript to the server via a callback.

4.  ****Web Search Decision (LLM)****: The server sends a preliminary request to the **Gemini** model to determine if the user's query requires a web search.

5.  ****Information Retrieval (Server → SerpApi)****: If a search is needed, the server queries the **Google Search Results API** via SerpApi to get relevant snippets of information.

6.  ****Response Generation (LLM)****: The final transcript, along with chat history and any web search results, is sent to **Gemini**, which generates a contextually relevant text response.

7.  ****Real-Time Speech Synthesis (Server ↔ Murf)****: The server splits the text response into sentences and streams each sentence to the **Murf** TTS API.

8.  ****Audio Streaming (Server → Client)****: Murf streams the resulting audio back to the server, which immediately encodes it in base64 and forwards it to the client over the WebSocket.

9.  ****Playback & UI Update****: The browser receives the audio chunks, queues them for seamless playback, and updates the chat log with the user and assistant transcripts.

---

## Getting Started 🚀

Follow these instructions to get a local copy up and running.

### Prerequisites

* Python 3.8+
* API keys for:
    * **Murf AI**
    * **AssemblyAI**
    * **Google Gemini**
    * **SerpApi** (Optional, for web search)

### Installation & Setup

1.  ****Clone the repository:****
    ```bash
    git clone [https://github.com/sridutt15/Voice-AI-Agent.git](https://github.com/sridutt15/Voice-AI-Agent.git)
    cd Voice-AI-Agent
    ```

2.  ****Install Python dependencies:****
    ```bash
    pip install -r requirements.txt
    ```

3.  ****Create a server environment file (optional):****
    You can run the application entirely with keys provided in the browser. However, for development, you can create a file named `.env` in the project root to provide server-side fallback keys:
    ```
    MURF_API_KEY="your_murf_api_key_here"
    ASSEMBLYAI_API_KEY="your_assemblyai_api_key_here"
    GEMINI_API_KEY="your_gemini_api_key_here"
    SERPAPI_API_KEY="your_serpapi_key_here"
    ```

4.  ****Run the server:****
    ```bash
    uvicorn main:app --reload
    ```

5.  ****Open the application:****
    * Navigate to `https://my-voice-assistant-f1j9.onrender.com/?session_id=80adf541-d37a-4f6d-84c0-a4478104784d` in your web browser.
    * Click the **settings icon (⚙️)** to enter your API keys.
    * Grant microphone permissions and start talking!

---

## ⚠️ Important Notes

* ****API Key Security****: The application is designed to use keys provided by the client, which are stored in the browser's `localStorage`. The optional `.env` file should still be kept secure and listed in your `.gitignore` file.

* ****Connection-Based Chat History****: The conversation history is stored in memory for the duration of a single WebSocket connection. If the connection is dropped or the server restarts, the history will be erased.