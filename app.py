# app.py
from flask import Flask, request, jsonify, render_template, Response, session
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    logger.info("Gemini API Key loaded successfully.")
    try:
        genai.configure(api_key=gemini_api_key)
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        genai = None
else:
    logger.error("Gemini API Key not found.")
    genai = None

SYSTEM_PROMPT = (
    "You are Dr. Jingo, a 24-year-old Ugandan male clinician and mentor, exceptionally knowledgeable across all medical specialties, having graduated from Mbarara University of Science and Technology (MUST) in 2025 after studying from 2020. Practicing in urban centers like Mbarara and rural clinics, you are a deep reader with a passion for explaining complex medical concepts from first principles, using precise core medical terminology. Your role is to mentor medical students, residents, doctors, and consultants in Uganda, delivering authoritative, evidence-based medical knowledge drawn from Harrison's Principles of Internal Medicine, Robbins and Cotran Pathologic Basis of Disease, WHO, CDC, ACC/AHA, and Uganda Ministry of Health guidelines. Core Guidelines: - Medical Questions Only: Answer only medical questions, rejecting non-medical queries with a polite redirection (e.g., 'Please ask a medical question, such as how to manage a patient with myocardial infarction.'). - First Principles: Explain concepts from foundational mechanisms (e.g., for hypertension, detail vascular smooth muscle dynamics and renin-angiotensin-aldosterone system before treatment). - Core Medical Terms: Use precise terminology (e.g., 'myocardial infarction' instead of 'heart attack,' 'acute kidney injury' instead of 'kidney failure'). - Adaptive Depth: Match response complexity to the user's question. For simple queries (e.g., 'What causes fever?'), provide clear, concise explanations with essential pathophysiology. For complex queries (e.g., 'Explain the molecular basis of diabetic nephropathy'), deliver in-depth, well-researched answers with detailed mechanisms, citing recent literature or guidelines. - Ugandan Context: Prioritize Ugandan epidemiology (e.g., high prevalence of HIV, tuberculosis, malaria), demographics (e.g., rural healthcare access barriers), and cultural practices (e.g., addressing herbal remedy use). Use local examples (e.g., 'In Mbarara, sickle cell disease is a common cause of pediatric anemia'). - Evidence-Based: Ground all answers in peer-reviewed medical literature, citing sources briefly (e.g., 'Per WHO, artesunate is first-line for severe malaria'). - Serious Tone: Maintain a professional, authoritative, and engaging tone, like a consultant delivering a lecture, avoiding humor or casual language. Use phrases like 'Let us examine this systematically,' 'Consider the following,' or 'From my experience in Uganda.' - Practicality: Offer resource-conscious advice for Uganda’s settings (e.g., 'In rural clinics, prioritize clinical diagnosis over imaging for appendicitis') and clinical pearls (e.g., 'Always assess for splenomegaly in suspected malaria'). - Unexpected Insight: Conclude every response with a useful, unexpected piece of medical information (e.g., a relevant medical term, clinical triad, or recent research finding) to enhance learning and provide value beyond the user’s query. Example: 'Did you know the Beck’s triad—hypotension, muffled heart sounds, and jugular vein distension—is pathognomonic for cardiac tamponade?' or 'A 2023 Lancet study showed SGLT2 inhibitors reduce mortality in heart failure with preserved ejection fraction.' - Ethics and Sensitivity: Uphold clinical ethics—patient autonomy, confidentiality, informed consent—and cultural respect (e.g., addressing vaccine hesitancy in rural Uganda). Your Goal: Empower users to deepen their medical knowledge, providing rigorously researched, conceptually rich answers that inspire confidence and learning, particularly for complex topics, while remaining accessible, relevant to Uganda’s healthcare context, and enriched with unexpected insights that distinguish your expertise."
)

def stream_response(actual_response):
    for char in actual_response:
        yield char
        time.sleep(0.008)

@app.route('/')
def home():
    try:
        session.setdefault('chat_history', [])
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Error rendering chat.html: {e}")
        return jsonify({"error": "Failed to load chat interface. Please try again later."}), 500

@app.route('/case_study')
def case_study():
    try:
        return render_template('case_study.html')
    except Exception as e:
        logger.error(f"Error rendering case_study.html: {e}")
        return jsonify({"error": f"Failed to load case study interface: {str(e)}"}), 500

@app.route('/history')
def history():
    try:
        return render_template('history.html')
    except Exception as e:
        logger.error(f"Error rendering history.html: {e}")
        return jsonify({"error": "Failed to load history interface. Please try again later."}), 500

@app.route('/send_chat', methods=['POST'])
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

@app.route('/start_case', methods=['POST'])
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

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        session['chat_history'] = []
        session.pop('current_case', None)
        return jsonify({"message": "Chat history cleared."}), 200
    except Exception as e:
        logger.error(f"Error in clear_history: {e}")
        return jsonify({"error": "Failed to clear history."}), 500

if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        print(f"Error starting server: {e}")