from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import re

app = Flask(__name__)
CORS(app)

def call_gemini(query):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"summary": "API Key Missing", "ghost_truth": "N/A", "context": "Config", "actions": ["Set key in Vercel"]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": f"Analyze this: {query}"}]}],
        "systemInstruction": {
            "parts": [{
                "text": "Analyze the input. Use Google Search if a URL is provided. Return ONLY a valid JSON object with these exact keys: 'summary', 'ghost_truth', 'context', 'actions' (list of strings). Do not include markdown formatting, backticks, or the word 'json'. Just the raw JSON object."
            }]
        },
        "tools": [{"google_search": {}}]
        # We removed generationConfig JSON mode to allow Search tool to function
    }

    try:
        response = requests.post(url, json=payload, timeout=55)
        result = response.json()
        
        if 'candidates' in result:
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up the response in case it still includes markdown backticks
            clean_json = re.sub(r'```json|```', '', raw_text).strip()
            return json.loads(clean_json)
            
        return {
            "summary": "Source Verification Failed.",
            "ghost_truth": str(result.get('error', 'API Response Error')),
            "context": "Crawl Interrupted",
            "actions": ["Check if the URL is behind a paywall", "Paste text directly"]
        }
    except Exception as e:
        return {
            "summary": "The analysis engine hit a processing limit.",
            "ghost_truth": str(e),
            "context": "System Error",
            "actions": ["Retry the request", "Simplify the input query"]
        }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400
    
    result = call_gemini(query)
    return jsonify({"analysis": result})
