from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import time

app = Flask(__name__)
CORS(app)

def call_gemini(query):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"summary": "API Key Missing", "ghost_truth": "N/A", "context": "Config Error", "actions": ["Set GEMINI_API_KEY"]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    # We are adding Google Search back in so it can "read" the URL content
    payload = {
        "contents": [{"parts": [{"text": f"Carefully analyze this specific content/URL: {query}"}]}],
        "systemInstruction": {
            "parts": [{
                "text": "You are a Technical Intelligence Analyst. Analyze the provided content. If it is a URL, use your tools to read it. Return ONLY a JSON object: { \"summary\": \"(Deep synthesis)\", \"ghost_truth\": \"(The technical core/unspoken bias)\", \"context\": \"(Connection to current science/tech trends)\", \"actions\": [\"Step 1\", \"Step 2\", \"Step 3\"] }. Be precise and avoid generic fluff."
            }]
        },
        "tools": [{"google_search": {}}],
        "generationConfig": { "responseMimeType": "application/json" }
    }

    for i in range(2):
        try:
            # We give it a long timeout because reading science articles takes time
            response = requests.post(url, json=payload, timeout=50)
            result = response.json()
            if 'candidates' in result:
                raw_text = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(raw_text)
        except Exception as e:
            time.sleep(2)
            
    return {
        "summary": "The engine could not verify the source in time.",
        "ghost_truth": "Potential crawl block or high latency.",
        "context": "Analysis Failed",
        "actions": ["Copy-paste the text of the article instead of the URL", "Try a different source"]
    }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "Empty query"}), 400
    return jsonify({"analysis": call_gemini(query)})
