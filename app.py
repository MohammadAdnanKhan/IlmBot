from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from model.retriever import query_faiss
from model.generator import refine_with_gemini
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow all origins

limiter = Limiter(get_remote_address, app=app, default_limits=["10 per 15 minutes"])

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "IlmBot API is running!"})

@app.route("/chat/", methods=["POST"])
@limiter.limit("10 per 15 minutes")
def chat_with_bot():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing query parameter"}), 400

        query = data["query"]
        logging.info(f"Received query: {query}")

        heading, retrieved_text = query_faiss(query)
        
        if retrieved_text and retrieved_text.lower() != "no relevant results found.":
            refined_answer = refine_with_gemini(query, retrieved_text)
            return jsonify({
                "heading": heading,
                "retrieved_text": retrieved_text,
                "enhanced_response": refined_answer
            })

        return jsonify({
            "heading": None,
            "retrieved_text": "No relevant information found.",
            "enhanced_response": "No enhanced answer available."
        })
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Loaded PORT: {port}")
    app.run(host='0.0.0.0', port=port,  debug=False)
