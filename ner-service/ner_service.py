from flask import Flask, request, jsonify
import json
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

app = Flask(__name__)

# Load FoodBaseBERT
tokenizer = AutoTokenizer.from_pretrained("Dizex/FoodBaseBERT")
model = AutoModelForTokenClassification.from_pretrained("Dizex/FoodBaseBERT")
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="max")

def convert_float32(obj):
    """Convert numpy float32 to Python float for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_float32(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_float32(item) for item in obj]
    elif hasattr(obj, 'dtype') and obj.dtype == 'float32':
        return float(obj)
    return obj

@app.route('/ner', methods=['POST'])
def food_ner():
    try:
        raw_data = request.get_data(as_text=True)
        if not raw_data:
            return jsonify({'error': 'No data provided'}), 400

        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Run NER and log raw results
        results = ner_pipeline(text)
        print("Raw NER results:", results)
        foods = [entity['word'] for entity in results if entity['entity_group'] == 'FOOD']
        print("Filtered foods:", foods)
        serialized_results = convert_float32(results)
        return jsonify({'foods': foods, 'raw_results': serialized_results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)