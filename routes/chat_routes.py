# routes/chat_routes.py
from flask import Blueprint, request, jsonify, render_template, Response, session
import google.generativeai as genai
import time
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

def stream_response(actual_response):
    for char in actual_response:
        yield char
        time.sleep(0.008)

@chat_bp.route('/')
def home():
    try:
        session.setdefault('chat_history', [])
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Error rendering chat.html: {e}")
        return jsonify({"error": "Failed to load chat interface. Please try again later."}), 500

@chat_bp.route('/send_chat', methods=['POST'])
def send_chat():
    try:
        if not request.is_json:
            logger.warning("Invalid request: Content-Type must be application/json")
            return jsonify({"error": "Request must be JSON."}), 400

        data = request.get_json()
        user_message = data.get("question")

        if not isinstance(user_message, str) or not user_message.strip():
            logger.warning("Invalid user input: Must be a non-empty string")
            return jsonify({"error": "Please provide a valid text question."}), 400

        logger.info(f"User question: {user_message}")

        if not genai:
            logger.error("Gemini API not initialized")
            return jsonify({"error": "Clinical resources unavailable. Please check the API configuration."}), 500

        session['chat_history'].append({"user": user_message})
        history = session['chat_history'][-5:]
        content = SYSTEM_PROMPT + " Previous conversation: " + str(history) + " Current question: " + user_message

        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(content)

        if response and hasattr(response, 'text') and response.text:
            actual_response = response.text.strip()
        else:
            logger.warning("No valid response from Gemini API")
            actual_response = "Sorry, I couldn’t process that question. Please ask a medical question, such as a patient case or pathophysiology query."

        session['chat_history'].append({"bot": actual_response})
        logger.info(f"Dr. Jingo response: {actual_response[:100]}...")

        return Response(stream_response(actual_response), content_type='text/plain; charset=utf-8')

    except Exception as e:
        logger.error(f"Error in send_chat: {e}")
        return jsonify({"error": "Something went wrong. Please ask a medical question, like a patient case or concept explanation."}), 500