import os
from flask import Flask, render_template, request, jsonify
import translator

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the home page."""
    model_info = translator.get_model_info()
    return render_template('index.html', model_info=model_info)

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')

@app.route('/translate', methods=['POST'])
def translate_sentence():
    """Endpoint to translate English to French."""
    try:
        data = request.get_json()
        if not data or 'sentence' not in data:
            return jsonify({'error': 'No sentence provided.'}), 400
            
        sentence = data['sentence'].strip()
        
        if not sentence:
            return jsonify({'error': 'Please enter an English sentence.'}), 400
            
        # Get translation
        translated_text, unknown_words, status, time_ms = translator.translate(sentence)
        
        return jsonify({
            'translation': translated_text,
            'unknown_words': unknown_words,
            'status': status,
            'time_ms': time_ms
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
