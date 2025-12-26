from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# The API key is provided by the environment
API_KEY = "" 

def call_gemini(query):
    # Using the preview flash model for high speed and search grounding
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
    
    system_prompt = """
    Analyze the input and return a JSON object ONLY.
    Structure:
    {
      "summary": "Direct, high-impact synthesis (2-3 sentences)",
      "ghost_truth": "The hidden bias or unspoken context",
      "context": "How this relates to global trends using search grounding",
      "actions": ["Action 1", "Action 2", "Action 3"]
    }
    Be sophisticated, objective, and sharp.
    """

    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "tools": [{"google_search": {}}],
        "generationConfig": { "responseMimeType": "application/json" }
    }

    # Exponential backoff retry
    for i in range(5):
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_text)
        except:
            time.sleep(2**i)
            
    return {
        "summary": "Analysis timed out.",
        "ghost_truth": "N/A",
        "context": "Connection error.",
        "actions": ["Please try again."]
    }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    result = call_gemini(query)
    return jsonify({"analysis": result})
