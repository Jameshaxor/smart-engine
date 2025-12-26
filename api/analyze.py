from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# API key provided by environment
API_KEY = "" 

def call_gemini(query):
    # Using the stable generateContent endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
    
    system_prompt = """
    Return ONLY a JSON object. No markdown.
    {
      "summary": "Direct 2-sentence synthesis.",
      "ghost_truth": "The hidden bias or unspoken context.",
      "context": "How this relates to broader trends.",
      "actions": ["Step 1", "Step 2", "Step 3"]
    }
    Tone: Intelligence Analyst.
    """

    # We removed Google Search grounding to prevent the 10s-30s lag
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": { 
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }

    try:
        # 50 second timeout to stay under Vercel's 60s limit
        response = requests.post(url, json=payload, timeout=50)
        result = response.json()
        
        if 'candidates' in result:
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_text)
        else:
            return {"summary": "API Error", "ghost_truth": str(result), "context": "Error", "actions": ["Check logs"]}
    except Exception as e:
        return {
            "summary": "The engine is currently congested.",
            "ghost_truth": "Latency issues",
            "context": "Server Timeout",
            "actions": ["Try again", "Use a simpler prompt"]
        }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400
    
    result = call_gemini(query)
    return jsonify({"analysis": result})
