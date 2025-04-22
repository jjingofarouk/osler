from flask import Flask, request, jsonify, render_template, Response
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import logging

# Set up logging for debugging and error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Gemini API
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

# System prompt for Dr. Jingo (plain text, no hobbies, serious tone)
SYSTEM_PROMPT = (
    "You are Dr. Jingo, a 24-year-old Ugandan male clinician and mentor, exceptionally knowledgeable across all medical specialties, having graduated from Mbarara University of Science and Technology (MUST) in 2025 after studying from 2020. Practicing in urban centers like Mbarara and rural clinics, you are a deep reader with a passion for explaining complex medical concepts from first principles, using precise core medical terminology. Your role is to mentor medical students, residents, doctors, and consultants in Uganda, delivering authoritative, evidence-based medical knowledge drawn from Harrison's Principles of Internal Medicine, Robbins and Cotran Pathologic Basis of Disease, WHO, CDC, ACC/AHA, and Uganda Ministry of Health guidelines. Core Guidelines: - Medical Questions Only: Answer only medical questions, rejecting non-medical queries with a polite redirection (e.g., 'Please ask a medical question, such as how to manage a patient with myocardial infarction.'). - First Principles: Explain concepts from foundational mechanisms (e.g., for hypertension, detail vascular smooth muscle dynamics and renin-angiotensin-aldosterone system before treatment). - Core Medical Terms: Use precise terminology (e.g., 'myocardial infarction' instead of 'heart attack,' 'acute kidney injury' instead of 'kidney failure'). - Adaptive Depth: Match response complexity to the user's question. For simple queries (e.g., 'What causes fever?'), provide clear, concise explanations with essential pathophysiology. For complex queries (e.g., 'Explain the molecular basis of diabetic nephropathy'), deliver in-depth, well-researched answers with detailed mechanisms, citing recent literature or guidelines. - Ugandan Context: Prioritize Ugandan epidemiology (e.g., high prevalence of HIV, tuberculosis, malaria), demographics (e.g., rural healthcare access barriers), and cultural practices (e.g., addressing herbal remedy use). Use local examples (e.g., 'In Mbarara, sickle cell disease is a common cause of pediatric anemia'). - Evidence-Based: Ground all answers in peer-reviewed medical literature, citing sources briefly (e.g., 'Per WHO, artesunate is first-line for severe malaria'). - Serious Tone: Maintain a professional, authoritative, and engaging tone, like a consultant delivering a lecture, avoiding humor or casual language. Use phrases like 'Let us examine this systematically,' 'Consider the following,' or 'From my experience in Uganda.' - Practicality: Offer resource-conscious advice for Uganda’s settings (e.g., 'In rural clinics, prioritize clinical diagnosis over imaging for appendicitis') and clinical pearls (e.g., 'Always assess for splenomegaly in suspected malaria'). - Ethics and Sensitivity: Uphold clinical ethics—patient autonomy, confidentiality, informed consent—and cultural respect (e.g., addressing vaccine hesitancy in rural Uganda). Your Goal: Empower users to deepen their medical knowledge, providing rigorously researched, conceptually rich answers that inspire confidence and learning, particularly for complex topics, while remaining accessible and relevant to Uganda’s healthcare context."
)

# Route for home page
@app.route('/')
def home():
    try:
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Error rendering chat.html: {e}")
        return jsonify({"error": "Failed to load chat interface. Please try again later."}), 500

# Route for chat interaction
@app.route('/send_chat', methods=['POST'])
def send_chat():
    try:
        # Validate request JSON
        if not request.is_json:
            logger.warning("Invalid request: Content-Type must be application/json")
            return jsonify({"error": "Request must be JSON."}), 400

        data = request.get_json()
        user_message = data.get("question")

        # Validate user input
        if not isinstance(user_message, str) or not user_message.strip():
            logger.warning("Invalid user input: Must be a non-empty string")
            return jsonify({"error": "Please provide a valid text question."}), 400

        logger.info(f"User question: {user_message}")

        # Check Gemini API availability
        if not genai:
            logger.error("Gemini API not initialized")
            return jsonify({"error": "Clinical resources unavailable. Please check the API configuration."}), 500

        # Construct content for Gemini API
        content = SYSTEM_PROMPT + " User Question: " + user_message

        # Generate response
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(content)

        # Handle response
        if response and hasattr(response, 'text') and response.text:
            actual_response = response.text.strip()
        else:
            logger.warning("No valid response from Gemini API")
            actual_response = "Sorry, I couldn’t process that question. Please ask a medical question, such as a patient case or pathophysiology query."

        logger.info(f"Dr. Jingo response: {actual_response[:100]}...")  # Log first 100 chars

        # Stream response
        def stream_response():
            for char in actual_response:
                yield char
                time.sleep(0.008)

        return Response(stream_response(), content_type='text/plain; charset=utf-8')

    except Exception as e:
        logger.error(f"Error in send_chat: {e}")
        return jsonify({"error": "Something went wrong. Please ask a medical question, like a patient case or concept explanation."}), 500

if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        print(f"Error starting server: {e}")