# routes/case_study_routes.py
from flask import Blueprint, render_template, jsonify, session, Response
from routes.utils import genai, SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

case_study_bp = Blueprint('case_study', __name__)

@case_study_bp.route('/case_study')
def case_study():
    try:
        session.setdefault('chat_history', [])  # Initialize chat_history if not set
        return render_template('case_study.html')
    except Exception as e:
        logger.error(f"Error rendering case_study.html: {e}")
        return jsonify({"error": f"Failed to load case study interface: {str(e)}"}), 500

@case_study_bp.route('/start_case', methods=['POST'])
def start_case():
    try:
        case_prompt = "Generate a clinical case for a medical student in Uganda, including patient history, symptoms, and a question for diagnosis. Provide a detailed scenario and ask the user to propose a differential diagnosis or next steps."
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(case_prompt)
        session['current_case'] = response.text
        session['chat_history'].append({"bot": response.text})
        return Response(response.text, content_type='text/plain; charset=utf-8')
    except Exception as e:
        logger.error(f"Error in start_case: {e}")
        return jsonify({"error": "Failed to generate case. Please try again."}), 500