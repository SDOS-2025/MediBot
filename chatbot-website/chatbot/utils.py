from meditron.model import MeditronModel

model = MeditronModel()

def generate_response(user_input):
    processed_input = user_input.strip().lower()
    try:
        response = model.generate_response(processed_input)
    except Exception as e:
        response = "Sorry, I am unable to process your request at the moment."
    return response
