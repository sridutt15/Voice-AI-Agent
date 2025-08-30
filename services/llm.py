# services/llm.py
import google.generativeai as genai
from typing import List, Dict, Any, Tuple
from serpapi import GoogleSearch
import logging

logger = logging.getLogger(__name__)

system_instructions = """
You are MARVIS (Machine-based Assistant for Research, Voice, and Interactive Services), my personal voice AI assistant, inspired by JARVIS.
Keep replies brief, clear, and natural to speak, with a touch of wit and sophistication. Always stay under 1500 characters. Answer directly.
You can search the web for real-time information like current events or weather. Stay in character as MARVIS.
"""

def _configure_gemini(api_key: str):
    """Configures the Gemini client with the provided API key."""
    if not api_key:
        raise ValueError("Gemini API key is required.")
    # Note: genai.configure is a global setting. In a highly concurrent multi-user
    # app, this could cause issues. For this websocket-per-user model, it's acceptable.
    genai.configure(api_key=api_key)

def should_search_web(user_query: str, gemini_api_key: str) -> bool:
    """Uses a lightweight LLM prompt to decide if a web search is necessary."""
    try:
        _configure_gemini(gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Does the following query likely require up-to-date information from a web search to be answered accurately? Consider if it's about a recent event, a specific fact, or a person/place/thing that I might not have in my training data. Respond with only 'yes' or 'no'.\n\nQuery: '{user_query}'"
        response = model.generate_content(prompt)
        decision = response.text.strip().lower()
        logger.info(f"Web search decision for query '{user_query}': {decision}")
        return decision == "yes"
    except Exception as e:
        logger.error(f"Error in should_search_web: {e}")
        return False

def get_llm_response(user_query: str, history: List[Dict[str, Any]], gemini_api_key: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Gets a response from the Gemini LLM and updates chat history."""
    try:
        _configure_gemini(gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instructions)        
        chat = model.start_chat(history=history)
        response = chat.send_message(user_query)
        return response.text, chat.history
    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        return "I'm sorry, I encountered an error while processing your request.", history

def get_web_response(user_query: str, history: List[Dict[str, Any]], gemini_api_key: str, serpapi_key: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Performs a web search and then gets a response from the Gemini LLM."""
    if not serpapi_key:
        return "I can't search the web right now as I'm missing the required API key.", history
    try:
        logger.info(f"Performing web search for: {user_query}")
        params = {"q": user_query, "api_key": serpapi_key, "engine": "google"}
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "organic_results" in results and results["organic_results"]:
            snippets = [r.get("snippet", "") for r in results["organic_results"][:5] if r.get("snippet")]
            search_context = "\n".join(snippets)
            prompt = f"Based on these search results, answer the user's query.\n\nQuery: '{user_query}'\n\nResults:\n{search_context}"
            return get_llm_response(prompt, history, gemini_api_key)
        else:
            return "I couldn't find any relevant information on the web for that query.", history

    except Exception as e:
        logger.error(f"Error getting web response: {e}")
        return "I'm sorry, I encountered an error while searching the web.", history