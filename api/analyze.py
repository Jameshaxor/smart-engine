from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

API_KEY = "" 

def call_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
    
    system_prompt = """
    Analyze the input and return ONLY a JSON object.
    {
      "summary": "2-3 sentence high-impact synthesis.",
      "ghost_truth": "The hidden bias/context.",
      "context": "Connection to global trends.",
      "actions": ["Step 1", "Step 2", "Step 3"]
    }
    """

    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "tools": [{"google_search": {}}],
        "generationConfig": { "responseMimeType": "application/json" }
    }

    # Reduced retries for faster failure/response
    for i in range(2):
        try:
            response = requests.post(url, json=payload, timeout=25)
            result = response.json()
            if 'candidates' in result:
                raw_text = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(raw_text)
        except Exception as e:
            if i == 0: time.sleep(1)
            continue
            
    return {
        "summary": "Intelligence gathering took too long. The source might be too complex or the API is congested.",
        "ghost_truth": "Indeterminate",
        "context": "System Latency",
        "actions": ["Try a shorter query", "Check if the URL is accessible", "Retry in a few moments"]
    }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query"}), 400
    
    result = call_gemini(query)
    return jsonify({"analysis": result})
