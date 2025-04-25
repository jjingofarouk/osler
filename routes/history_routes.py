# routes/history_routes.py
from flask import Blueprint, render_template, jsonify, session
import logging

logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
def history():
    try:
        return render_template('history.html')
    except Exception as e:
        logger.error(f"Error rendering history.html: {e}")
        return jsonify({"error": "Failed to load history interface. Please try again later."}), 500

@history_bp.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        session['chat_history'] = []
        session.pop('current_case', None)
        return jsonify({"message": "Chat history cleared."}), 200
    except Exception as e:
        logger.error(f"Error in clear_history: {e}")
        return jsonify({"error": "Failed to clear history."}), 500