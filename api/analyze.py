from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

def call_gemini(query):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"summary": "API Key Missing", "ghost_truth": "N/A", "context": "Config", "actions": ["Check Vercel Env"]}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    # We use a more direct instruction to prevent the model from over-searching
    payload = {
        "contents": [{"parts": [{"text": f"Analyze this input: {query}"}]}],
        "systemInstruction": {
            "parts": [{
                "text": "You are a Strategic Intelligence Analyst. If a URL is provided, use your search tool to extract its core content. Perform a deep synthesis. Return ONLY a JSON object: { \"summary\": \"High-level synthesis (2-3 sentences)\", \"ghost_truth\": \"The technical reality or unspoken bias\", \"context\": \"Broader industry/science context\", \"actions\": [\"Strategic step 1\", \"Strategic step 2\", \"Strategic step 3\"] }."
            }]
        },
        "tools": [{"google_search": {}}],
        "generationConfig": { 
            "responseMimeType": "application/json",
            "temperature": 0.2 # Lower temperature for more focused analysis
        }
    }

    try:
        # Set timeout to 55s to give Flask a chance to return before Vercel kills it at 60s
        response = requests.post(url, json=payload, timeout=55)
        result = response.json()
        
        if 'candidates' in result:
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_text)
            
        return {
            "summary": "The API returned an unexpected response.",
            "ghost_truth": str(result.get('error', 'Unknown API Error')),
            "context": "Analysis Interrupted",
            "actions": ["Verify the URL is public", "Try pasting the text directly"]
        }
    except Exception as e:
        return {
            "summary": "The source is taking too long to verify.",
            "ghost_truth": "High latency on the source website.",
            "context": "Timeout",
            "actions": ["Copy the article text and paste it here", "Try a shorter URL"]
        }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400
    
    result = call_gemini(query)
    return jsonify({"analysis": result})
