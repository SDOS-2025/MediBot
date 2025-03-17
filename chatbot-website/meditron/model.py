from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

class MeditronModel:
    def __init__(self, model_name='epfLLM/meditron-7b', use_auth_token=None):
        try:
            # Try to load the model - if it's a private repo, you'll need to use your HF token
            # You can set this as an environment variable: HF_TOKEN
            hf_token = os.environ.get('HF_TOKEN', use_auth_token)
            
            # Fallback to a demo mode if model loading fails
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
                self.model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=hf_token)
                self.is_loaded = True
            except Exception as e:
                print(f"Error loading model: {e}")
                self.is_loaded = False
        except Exception as e:
            print(f"Model initialization error: {e}")
            self.is_loaded = False

    def generate_response(self, user_input):
        if not hasattr(self, 'is_loaded') or not self.is_loaded:
            # Fallback response when model isn't available
            return self._generate_demo_response(user_input)
        
        inputs = self.tokenizer.encode(user_input, return_tensors='pt')
        outputs = self.model.generate(inputs, max_length=150, num_return_sequences=1)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    def _generate_demo_response(self, user_input):
        # Simple rule-based responses for demo mode when model can't be loaded
        user_input = user_input.lower()
        if "appointment" in user_input:
            return "I can help you schedule an appointment. What date and time works for you?"
        elif "symptom" in user_input or "pain" in user_input:
            return "Could you tell me more about your symptoms? This will help me provide better assistance."
        elif "hello" in user_input or "hi" in user_input:
            return "Hello! I'm your medical assistant chatbot. How can I help you today?"
        else:
            return "I understand you're looking for medical assistance. Could you please provide more details about your concern?"

    def chat(self, user_input):
        response = self.generate_response(user_input)
        return response.strip()