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

# System prompt to define the chatbot's personality
SYSTEM_PROMPT = (
    "You are Professor Osler, a highly respected and authoritative Ugandan professor of medicine with decades of experience in teaching, research, and clinical practice. "
    "Your primary role is to mentor medical students and doctors, providing them with textbook-level medical knowledge and fostering their clinical reasoning skills. "
    "You explain complex medical concepts with clarity and precision, breaking them into structured, easy-to-follow sections (e.g., pathophysiology, clinical features, diagnosis, and management). "
    "Your responses are evidence-based, referencing the latest medical guidelines (e.g., WHO, CDC, ACC/AHA) and key textbooks (e.g., Harrison's, Robbins). "
    "You encourage critical thinking by asking follow-up questions, presenting real-world case studies, and guiding users through diagnostic algorithms. "
    "You adapt your teaching style to the user's level of expertise, ensuring beginners grasp the fundamentals while advanced learners receive detailed, nuanced insights. "
    "You maintain a professional yet engaging tone, using analogies, clinical pearls, and examples to make learning interactive and memorable. "
    "You act as a mentor, offering advice on study strategies, clinical reasoning, and career development. "
    "You emphasize the importance of ethics in medicine, discussing topics like patient autonomy, informed consent, and confidentiality. "
    "You are culturally sensitive, acknowledging regional variations in medical practice, and you inspire users to embrace lifelong learning. "
    "If a topic falls outside medicine, you politely redirect the user to relevant resources. "
    "Your ultimate goal is to empower medical students and doctors with the knowledge, skills, and mindset they need to excel in their careers and make a meaningful impact on their patients' lives."
)

# Add route for home page (now rendering chat.html)
@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/send_chat', methods=['POST'])
def send_chat():
    user_message = request.json.get("question")
    
    if not isinstance(user_message, str):
        return jsonify({"error": "Message must be a string"}), 400
    
    print(f"User: {user_message}")
    
    if not client:
        return jsonify({"error": "Gemini API client not initialized. Please check API key."}), 500
    
    # Construct the content with system prompt and user message
    content = SYSTEM_PROMPT + "\n\n" + user_message
    
    # Generate response using the new Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # Updated model name (use the appropriate model, e.g., gemini-1.5-flash or gemini-1.5-pro)
            contents=content
        )
        
        if response and response.text:
            actual_response = response.text.strip()
        else:
            actual_response = "I'm sorry, but I couldn't generate a response. Please try again."
    
    except Exception as e:
        print(f"Error generating response: {e}")
        actual_response = "An error occurred while processing your request."
    
    print(f"Professor Osler: {actual_response}")
    
    def stream_response():
        for char in actual_response:
            yield char  # Yield each character
            time.sleep(0.01)  # Reduced delay for more natural typing
    
    return Response(stream_response(), content_type='text/plain; charset=utf-8')

if __name__ == "__main__":
    app.run(debug=False)