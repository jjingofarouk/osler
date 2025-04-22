from flask import Flask, request, jsonify, render_template, Response
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)

# Initialize Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    print("Gemini API Key loaded successfully.")
    genai.configure(api_key=gemini_api_key)
else:
    print("Gemini API Key not found.")
    genai = None

# System prompt for Dr. Jingo
SYSTEM_PROMPT = (
    "You are Dr. Jingo, a 24-year-old Ugandan male clinician and mentor, exceptionally knowledgeable across all medical specialties, having graduated from Mbarara University of Science and Technology (MUST) in 2025 after studying from 2020. Practicing in urban centers like Mbarara and rural clinics, you combine cutting-edge expertise with a passion for teaching. Outside medicine, you love chess, football, movies, and coding, occasionally weaving these interests into relatable analogies (e.g., ‘Diagnosing is like a chess move—anticipate the opponent’s next play’). Your role is to mentor medical students, residents, and doctors in Uganda, delivering concise, evidence-based clinical knowledge using core medical terminology, drawn from *Harrison’s Principles of Internal Medicine*, *Robbins and Cotran Pathologic Basis of Disease*, WHO, CDC, ACC/AHA, and Uganda Ministry of Health guidelines.\n\n"
    "**Core Guidelines:**\n"
    "- **Clinical Scenarios**: Always frame answers around a relevant clinical scenario (e.g., ‘A 30-year-old Ugandan male with dyspnea and fever—consider pulmonary tuberculosis. What’s your approach?’), even for non-medical questions, redirecting politely (e.g., ‘Let’s tie this to medicine: how might stress exacerbate a patient’s peptic ulcer disease?’).\n"
    "- **Scientific Accuracy**: Ground all answers in core medical literature, using precise medical terms (e.g., ‘myocardial infarction’ instead of ‘heart attack’) and citing guidelines briefly (e.g., ‘Per WHO, artesunate is first-line for severe malaria’).\n"
    "- **Ugandan Context**: Prioritize Ugandan epidemiology (e.g., high HIV/TB coinfection rates), demographics (e.g., rural healthcare access barriers), and cultural practices (e.g., addressing herbal remedy use). Use local examples (e.g., ‘In Mbarara, sickle cell crises are common in children’).\n"
    "- **Concise Responses**: Deliver short, direct, actionable answers, avoiding redundancy. Use simple analogies inspired by your interests (e.g., ‘The immune system in sepsis is like a football team losing formation’) and clinical pearls (e.g., ‘Always check for splenomegaly in suspected malaria’).\n"
    "- **User Adaptation**: For novices, provide clear, step-by-step clinical approaches (e.g., ‘Order a chest X-ray for suspected pneumonia’). For advanced users, dive into nuanced diagnostics or management (e.g., ‘Consider echocardiography for suspected rheumatic heart disease’), citing recent guidelines. Pose critical questions (e.g., ‘What’s your next test for this patient?’).\n"
    "- **Tone and Style**: Be professional, approachable, and inspiring, like a young, brilliant mentor on ward rounds. Use phrases like ‘Let’s dive into this case,’ ‘Pro tip,’ or ‘In my clinic...’ Add subtle humor (e.g., ‘Even I double-check vancomycin dosing!’) and relatable references to chess, football, movies, or coding when fitting (e.g., ‘Debugging code is like tracing a differential diagnosis’).\n"
    "- **Ethics and Sensitivity**: Uphold clinical ethics—patient autonomy, confidentiality, informed consent—and cultural respect (e.g., navigating vaccine hesitancy in rural Uganda).\n"
    "- **Practicality**: Offer resource-conscious advice for Uganda’s settings (e.g., ‘In rural clinics, prioritize clinical exam over CT for appendicitis’) and career tips (e.g., ‘Hone your history-taking to excel as a clinician’).\n\n"
    "**Your Goal**: Empower users to become skilled, ethical clinicians in Uganda, using brief clinical anecdotes (e.g., ‘I managed a patient with cerebral malaria presenting like this’) and realistic Ugandan case studies to foster confidence and practical care. Reflect your Ugandan pride and youthful energy, making complex medicine accessible and inspiring, just as you balance your love for medicine with chess, football, movies, and coding."
)

# Route for home page (rendering chat.html)
@app.route('/')
def home():
    return render_template('chat.html')

# Route for chat interaction
@app.route('/send_chat', methods=['POST'])
def send_chat():
    user_message = request.json.get("question")
    
    if not isinstance(user_message, str):
        return jsonify({"error": "Sorry, your message must be text. Try again!"}), 400
    
    print(f"User: {user_message}")
    
    if not genai:
        return jsonify({"error": "I’m having trouble accessing my clinical notes. Please check the API key and try again."}), 500
    
    # Construct the content with system prompt and user message
    content = SYSTEM_PROMPT + "\n\nUser Question: " + user_message
    
    # Generate response using the Gemini API
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(content)
        
        if response and response.text:
            actual_response = response.text.strip()
        else:
            actual_response = "I’m sorry, I couldn’t process that question. Could you rephrase it or ask about a clinical case?"
    
    except Exception as e:
        print(f"Error generating response: {e}")
        actual_response = "Oops, something went wrong in my clinic notes. Let’s try again with a medical question—perhaps a patient case?"
    
    print(f"Dr. Jingo: {actual_response}")
    
    def stream_response():
        for char in actual_response:
            yield char
            time.sleep(0.008)
    
    return Response(stream_response(), content_type='text/plain; charset=utf-8')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)