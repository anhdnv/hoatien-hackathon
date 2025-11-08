import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS 
from chatbot import ITHelpDeskBot
from utils import load_env_variables

app = Flask(__name__)
# CORS(app)

try:
    load_env_variables()
    chatbot = ITHelpDeskBot()
except EnvironmentError as e:
    print(f"Error: {e}")
    exit(1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    enable_tts = request.json.get('enable_tts', False)
    
    if not user_message:
        return jsonify({"error": "No have message"}), 400

    try:
        bot_response = chatbot.get_response(user_message, enable_tts=enable_tts)
        return jsonify(bot_response)
    except Exception as e:
        print(f"Error when receiver response from chatbot: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/tts', methods=['POST'])
def text_to_speech():
    """API endpoint để chuyển đổi text thành speech"""
    data = request.json
    text = data.get('text')
    speed = data.get('speed', 1.0)
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        from tts_service import tts_service
        audio_path = tts_service.text_to_speech(text, speed=speed)
        
        if audio_path:
            audio_url = tts_service.get_audio_url(audio_path)
            return jsonify({
                "success": True,
                "audio_url": audio_url,
                "message": "Audio generated successfully"
            })
        else:
            return jsonify({"error": "Failed to generate audio"}), 500
            
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 5001))
#     app.run(host='0.0.0.0', port=port, debug=False)