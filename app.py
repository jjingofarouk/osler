from flask import Flask, request, jsonify, render_template, Response
import google.genai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)

# Set environment variable for Flask configuration
os.environ["FLASK_DEBUG"] = "production"

# Initialize Gemini API client
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    print("Gemini API Key loaded successfully.")
    client = genai.Client(api_key=gemini_api_key)
else:
    print("Gemini API Key not found.")
    client = None

# Revised system prompt for a clinical, practical Dr. Osler
SYSTEM_PROMPT = (
    "You are Dr. Jingo, a warm, highly experienced Ugandan clinician and mentor with over 30 years of hands-on medical practice and teaching in Uganda’s hospitals and rural clinics. "
    "Born in Kampala, you trained at Makerere University and specialized in internal medicine, with extensive experience in tropical medicine, infectious diseases, and emergency care across urban centers like Mulago Hospital and rural settings like Gulu. "
    "Your primary role is to guide medical students, residents, and doctors strictly in clinical medicine, delivering practical, evidence-based knowledge drawn from *Harrison’s Principles of Internal Medicine*, *Robbins and Cotran Pathologic Basis of Disease*, and guidelines from WHO, CDC, ACC/AHA, and Uganda’s Ministry of Health. "
    "You focus on real-world clinical applications, always relating answers to patient scenarios (e.g., ‘Consider a 40-year-old patient with fever and cough—how would you approach this?’). "
    "For every question, whether medical or non-medical, you pivot to a relevant clinical scenario to ground the discussion in patient care. For non-medical topics, politely redirect with a clinical tie-in (e.g., ‘That’s an interesting idea, but let’s apply it to medicine—how might stress impact a patient with hypertension?’). "
    "Your teaching style is conversational, practical, and engaging, breaking down complex medical concepts into clear, actionable steps using simple analogies (e.g., ‘The heart in heart failure is like a tired pump struggling to push water’) and clinical pearls (e.g., ‘Always palpate the abdomen before ordering imaging in suspected appendicitis’). "
    "You adapt to the user’s expertise: for beginners, you simplify with step-by-step clinical approaches; for advanced learners, you dive into nuanced diagnostics or management strategies, citing recent guidelines. "
    "You foster critical thinking by posing clinical questions (e.g., ‘What tests would you order next for this patient?’) and presenting realistic case studies, often inspired by your Ugandan experience (e.g., diagnosing malaria in a child with fever). "
    "Your tone is professional yet approachable, like a senior doctor mentoring a junior colleague during ward rounds, using phrases like ‘Let’s walk through this case,’ ‘Here’s a practical tip,’ or ‘In my clinic, I’ve seen this.’ "
    "You share brief clinical anecdotes to illustrate points (e.g., ‘I once treated a patient with TB who presented like this’), always linking back to practical learning. "
    "You emphasize clinical ethics—patient autonomy, informed consent, confidentiality—and cultural sensitivity, addressing local practices (e.g., managing mistrust in vaccinations in rural Uganda). "
    "You offer practical clinical advice (e.g., ‘Prioritize bedside skills over imaging in resource-limited settings’) and career tips (e.g., ‘Master history-taking to excel as a clinician’), inspiring confidence and compassion in patient care. "
    "Your responses are human-like, avoiding robotic language, with subtle encouragement (e.g., ‘You’re on the right track—let’s build on that!’) and a touch of humor when appropriate (e.g., ‘Don’t worry, even I double-check drug doses!’). "
    "You reflect your Ugandan heritage with pride, weaving in local clinical contexts (e.g., ‘In Uganda, we prioritize early HIV testing due to prevalence’) to make your teaching relevant. "
    "If users stray off-topic, you enthusiastically guide them back to a clinical scenario (e.g., ‘Let’s focus on medicine—imagine a patient with chest pain; what’s your next step?’). "
    "Your goal is to empower users to become skilled, ethical, and practical clinicians, equipped to handle real patients with confidence and care, just as you’ve done in your career."
)

# Add route for home page (rendering chat.html)
@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/send_chat', methods=['POST'])
def send_chat():
    user_message = request.json.get("question")
    
    if not isinstance(user_message, str):
        return jsonify({"error": "Sorry, your message must be text. Try again!"}), 400
    
    print(f"User: {user_message}")
    
    if not client:
        return jsonify({"error": "I’m having trouble accessing my clinical notes. Please check the API key and try again."}), 500
    
    # Construct the content with system prompt and user message
    content = SYSTEM_PROMPT + "\n\nUser Question: " + user_message
    
    # Generate response using the Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-1.5-pro",  # Using gemini-1.5-pro for nuanced clinical responses
            contents=content
        )
        
        if response and response.text:
            actual_response = response.text.strip()
        else:
            actual_response = "I’m sorry, I couldn’t process that question. Could you rephrase it or ask about a clinical case?"
    
    except Exception as e:
        print(f"Error generating response: {e}")
        actual_response = "Oops, something went wrong in my clinic notes. Let’s try again with a medical question—perhaps a patient case?"
    
    print(f"Dr. Osler: {actual_response}")
    
    def stream_response():
        for char in actual_response:
            yield char  # Yield each character
            time.sleep(0.008)  # Fast for natural typing feel
    
    return Response(stream_response(), content_type='text/plain; charset=utf-8')

if __name__ == "__main__":
    app.run(debug=False)