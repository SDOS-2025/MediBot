from chatbot.ai_wrapper import send_chat_message, generate_medical_report

def generate_response(user_input):
    processed_input = user_input.strip()
    try:
        response = send_chat_message(processed_input)
    except Exception as e:
        response = "Sorry, I am unable to process your request at the moment."
    return response


from reportlab.pdfgen import canvas
from io import BytesIO
import os
from django.conf import settings
import random

def generate_sample_text():
    # Generate random medical report text
    symptoms = ["headache", "fever", "cough", "fatigue"]
    diagnoses = ["common cold", "influenza", "migraine", "viral infection"]
    return f"""
    Patient Report:
    Name: Patient #{random.randint(1000, 9999)}
    Symptoms: {random.sample(symptoms, 2)}
    Diagnosis: {random.choice(diagnoses)}
    Recommendations: Rest and hydration
    """
# chatbot/utils.py
def text_to_pdf(text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    
    # Add creation date
    from datetime import datetime
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Enhanced styling
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(300, 800, "Official Medical Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 775, f"Generated: {creation_date}")
    
    # Content formatting
    y_position = 750
    for line in text.split('\n'):
        if line.strip().startswith("Patient Report:"):
            pdf.setFont("Helvetica-Bold", 14)
        else:
            pdf.setFont("Helvetica", 12)
            
        pdf.drawString(50, y_position, line.strip())
        y_position -= 20
    
    pdf.save()
    
    # Generate filename with timestamp
    filename = f"report_{random.randint(1000,9999)}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filename