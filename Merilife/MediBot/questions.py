from google import genai
from google.genai import types

# Initialize the Gemini client
client = genai.Client(api_key="AIzaSyB0R26JpwnrxR1iHP7SRdlXImYhG2NAYLQ")

# System instruction for the medical assistant chatbot with delimiter
system_instruction = (
    "You are a medical assistant chatbot. Follow this EXACT process:"
    "\n1. Ask the patient: 'What are your main symptoms?'"
    "\n2. Ask the patient: 'How long have you been experiencing these symptoms?'"
    "\n3. Ask the patient: 'Do you have any previous medical conditions?'"
    "\n4. Based on all previous answers, ask ONE relevant follow-up question."
    "\n5. Based on all previous answers, ask ONE final relevant follow-up question."
    "\nAfter collecting all answers, generate a medical report with sections for History of Present Illness, "
    "Medications, and Allergies. Then include the delimiter '###1234###' on a new line, followed by your preliminary diagnosis."
    "\nDo NOT ask multiple questions at once. Ask EXACTLY ONE question at a time and wait for the answer."
)

# Create the chat
chat = client.chats.create(
    model="gemini-1.5-flash",
    config=types.GenerateContentConfig(system_instruction=system_instruction)
)

# Fixed questions
fixed_questions = [
    "What are your main symptoms?",
    "How long have you been experiencing these symptoms?",
    "Do you have any previous medical conditions?"
]

# Main function to run the medical chatbot
def run_medical_chatbot():
    conversation = []
    
    # Ask fixed questions (Q1-Q3)
    for i, question in enumerate(fixed_questions):
        q_num = i + 1
        print(f"\nQ{q_num}: {question}")
        conversation.append(f"Q{q_num}: {question}")
        
        # Get user's answer
        answer = input(f"A{q_num}: ")
        conversation.append(f"A{q_num}: {answer}")
        
        # Send answer to the model
        chat.send_message(answer)
    
    # Generate Q4 based on previous conversation
    resp = chat.send_message("Based on the previous answers, ask your fourth question.")
    q4 = resp.text.strip()
    print(f"\nQ4: {q4}")
    conversation.append(f"Q4: {q4}")
    
    # Get user's answer for Q4
    a4 = input("A4: ")
    conversation.append(f"A4: {a4}")
    chat.send_message(a4)
    
    # Generate Q5 based on all previous conversation
    resp = chat.send_message("Based on all previous answers, ask your fifth and final question.")
    q5 = resp.text.strip()
    print(f"\nQ5: {q5}")
    conversation.append(f"Q5: {q5}")
    
    # Get user's answer for Q5
    a5 = input("A5: ")
    conversation.append(f"A5: {a5}")
    chat.send_message(a5)
    
    # Generate medical report and diagnosis with delimiter
    print("\nGenerating medical report and diagnosis based on all answers...")
    resp = chat.send_message(
        "Based on all the information provided, generate a comprehensive medical report with sections for History of Present Illness, "
        ", and Allergies. Then include the delimiter '###1234###' on a new line, followed by your preliminary diagnosis."
    )
    
    report_and_diagnosis = resp.text.strip()
    
    # Display the full conversation and the report
    print("\n=== CONVERSATION SUMMARY ===")
    for item in conversation:
        print(item)
    
    print("\n=== MEDICAL REPORT AND DIAGNOSIS ===")
    print(report_and_diagnosis)
    
    # Optionally split and display the report and diagnosis separately
    if "###1234###" in report_and_diagnosis:
        report, diagnosis = report_and_diagnosis.split("###1234###", 1)
        print("\n=== REPORT ONLY ===")
        print(report.strip())
        print("\n=== DIAGNOSIS ONLY ===")
        print(diagnosis.strip())

# Run the chatbot
if __name__ == "__main__":
    run_medical_chatbot()