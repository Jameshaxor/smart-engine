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
        return {"summary": "API Key Missing", "ghost_truth": "N/A", "context": "Config", "actions": ["Add key to Vercel"]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    # SYSTEM PROMPT: Optimized for speed and JSON reliability
    system_prompt = (
        "You are a Strategic Intelligence Analyst. "
        "Analyze the user input deeply. If it is a URL, use your internal knowledge to provide a high-fidelity summary. "
        "Return ONLY a raw JSON object with these keys: summary, ghost_truth, context, actions (list). "
        "No markdown, no backticks."
    )

    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4
        }
    }

    try:
        # Reduced timeout to 40s to ensure we respond before Vercel cuts us off
        response = requests.post(url, json=payload, timeout=40)
        
        if response.status_code != 200:
            return {
                "summary": "The Intelligence API rejected the request.",
                "ghost_truth": f"Status Code: {response.status_code}",
                "context": "API Limitation",
                "actions": ["Try a simpler prompt", "Wait 60 seconds and retry"]
            }

        result = response.json()
        if 'candidates' in result:
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            # Safety cleaning of the JSON string
            clean_json = re.sub(r'```json|```', '', raw_text).strip()
            return json.loads(clean_json)
            
        return {"summary": "Empty response from engine.", "ghost_truth": "N/A", "context": "No candidates found", "actions": ["Retry"]}
        
    except Exception as e:
        return {
            "summary": "Intelligence gathering exceeded the 60-second window.",
            "ghost_truth": str(e),
            "context": "Vercel Timeout",
            "actions": ["Copy the article text and paste it here instead of the URL", "Try again in a moment"]
        }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400
    return jsonify({"analysis": call_gemini(query)})
