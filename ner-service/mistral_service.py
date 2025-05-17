from flask import Flask, request, jsonify
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))  # Replace with key or use env var

# System prompt for food advisor
SYSTEM_PROMPT = """You are a food advisor AI for Fit'n Verdure, specializing in nutrition and healthy eating. Provide accurate, concise, and practical advice based on the user's input. If the input includes specific foods, tailor recommendations to those foods. For general questions, offer evidence-based nutritional guidance. Avoid harmful or unsafe advice. Keep responses under 200 words."""

@app.route('/advisor', methods=['POST'])
def food_advisor():
    try:
        raw_data = request.get_data(as_text=True)
        if not raw_data:
            return jsonify({'error': 'No data provided'}), 400
        data = json.loads(raw_data)
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Initialize Gemini model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

        # Generate response
        response = model.generate_content(
            text,
            generation_config={
                "max_output_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )

        # Extract text response
        advice = response.text.strip()
        return jsonify({'advice': advice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)