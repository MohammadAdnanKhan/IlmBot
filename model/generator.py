import os
import requests
from dotenv import load_dotenv
from model.retriever import query_faiss  # Assuming this is your FAISS integration

# Load environment variables
load_dotenv()
api_key = os.getenv("api_key")

if not api_key:
    raise ValueError("❌ Gemini API key not found. Set it as an environment variable named 'api_key'.")

def refine_with_gemini(query, retrieved_text):
    """Enhance FAISS output using Google Gemini (via REST API)"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    truncated_text = retrieved_text[:3000]

    prompt = f"""You are an AI historian named IlmBot, specializing in the life and teachings of Prophet Muhammad (PBUH).
Based on the query and retrieved content, provide a well-structured and engaging response.

- Do not introduce yourself unless explicitly asked.
- If the retrieved content does not fully match the query, prioritize answering the query accurately without mentioning retrieval mistakes.
- Ensure the response is concise, informative, and maintains historical accuracy.

**Query:** {query}
**Context:** {truncated_text}

Craft your response with clarity and relevance.
"""

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            return "❌ Failed to parse Gemini's response."
    else:
        print("❌ Gemini API error:", response.text)
        return "❌ Failed to generate content."

def query_chatbot(query):
    """Query FAISS and enhance response with Gemini"""
    score, heading, retrieved_text = query_faiss(query)

    if retrieved_text != "No relevant results found.":
        refined_answer = refine_with_gemini(query, retrieved_text)
        return score, retrieved_text, refined_answer
    else:
        return score, "No relevant information found.", "No enhanced answer available."

if __name__ == "__main__":
    query = "What was the first revelation received by Prophet Muhammad?"
    score, retrieved, answer = query_chatbot(query)

    print(f"\n🔹 **FAISS Score:** {score}")
    print(f"📖 **Retrieved Text:** {retrieved}")
    print(f"🤖 **IlmBot's Answer:** {answer}")
