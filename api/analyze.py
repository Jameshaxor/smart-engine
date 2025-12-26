from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# Vercel provides the API key in the environment variables automatically
# during the request cycle in this specific setup.
def get_api_key():
    # Attempt to get the key from environment variables
    return os.environ.get("GEMINI_API_KEY", "")

def call_gemini(query):
    api_key = get_api_key()
    if not api_key:
        return {
            "summary": "API Key Missing.",
            "ghost_truth": "The system requires an identity to process this request.",
            "context": "Configuration Error",
            "actions": ["Add GEMINI_API_KEY to Vercel Environment Variables"]
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": "Return ONLY a JSON object with keys: summary, ghost_truth, context, actions (list)."}]},
        "generationConfig": { "responseMimeType": "application/json" }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if 'candidates' in result:
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_text)
        return {"summary": "API Error", "ghost_truth": str(result), "context": "Error", "actions": ["Retry"]}
    except Exception as e:
        return {"summary": "Connection Error", "ghost_truth": str(e), "context": "Error", "actions": ["Retry"]}

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400
    
    result = call_gemini(query)
    return jsonify({"analysis": result})
