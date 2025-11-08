import os
import ssl
import certifi
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS 
from chatbot import ITHelpDeskBot
from utils import load_env_variables

# Set SSL certificate file
os.environ['SSL_CERT_FILE'] = certifi.where()

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
    language = request.json.get('language', 'vi')  # Default to Vietnamese
    
    if not user_message:
        return jsonify({"error": "No have message"}), 400

    try:
        bot_response = chatbot.get_response(user_message, language=language, enable_tts=False)
        return jsonify(bot_response)
    except Exception as e:
        print(f"Error when receiver response from chatbot: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
