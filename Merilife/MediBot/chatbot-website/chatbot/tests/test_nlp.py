from chatbot.speech_to_text import transcribe_audio  # Import from your app
from chatbot.utils import translate_input  # Import from your utils

def test_hindi_speech():
    # Place test audio in chatbot/tests/data/hindi_cold.wav
    with open('chatbot/tests/data/hindi_cold.wav', 'rb') as f:
        text = transcribe_audio(f.read(), lang='hi')
    assert 'cold' in text.lower()
# Add dummy translate_input in utils.py or implement actual translation
def translate_input(text, source_lang, target_lang):
    # Temporary dummy implementation
    return "headache" if text == "सिरदर्द" else text
def test_translation():
    translated = translate_input('सिरदर्द', 'hi', 'en')
    assert translated.lower() == 'headache'