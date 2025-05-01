"""
Speech to Text module using Google Speech Recognition.
This module provides functionality to convert audio to text using the SpeechRecognition library.
"""
import os
import wave
import logging
import tempfile
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for more verbose logging

# Try to import speech_recognition
try:
    import speech_recognition as sr
    from pydub import AudioSegment
    SPEECH_RECOGNITION_AVAILABLE = True
    logger.info("SpeechRecognition and pydub packages loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import speech recognition libraries: {e}")
    SPEECH_RECOGNITION_AVAILABLE = False

class SpeechToText:
    """
    Class for handling speech-to-text conversion using Google Speech Recognition.
    """
    def __init__(self):
        self.recognizer = None
        self.initialized = False
        
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.initialized = True
                logger.info("Speech recognition initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing speech recognition: {e}")
    
    def convert_audio_to_text(self, audio_file_path):
        """
        Converts audio file to text using Google Speech Recognition.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            str: Transcribed text or error message
        """
        if not self.initialized:
            logger.error("Speech recognition not initialized")
            return "Speech recognition not available. Please type your response."
        
        try:
            logger.debug(f"Processing audio file: {audio_file_path}")
            
            # Process directly if it's a WAV file
            if audio_file_path.lower().endswith('.wav'):
                try:
                    # Direct processing of WAV file
                    with sr.AudioFile(audio_file_path) as source:
                        logger.debug("Recording audio data from file")
                        audio_data = self.recognizer.record(source)
                        
                        logger.debug("Sending audio to Google Speech Recognition")
                        text = self.recognizer.recognize_google(
                            audio_data,
                            language="en-US",
                            show_all=False
                        )
                        logger.info(f"Transcription successful: '{text}'")
                        return text
                except Exception as direct_error:
                    logger.warning(f"Direct WAV processing failed: {direct_error}, trying alternative method...")
            
            # If not WAV or direct processing failed, try with pydub
            try:
                # Create a temporary WAV file
                temp_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                temp_wav_path = temp_wav_file.name
                temp_wav_file.close()
                
                logger.debug(f"Converting audio to WAV format: {temp_wav_path}")
                
                # Try to convert to WAV using pydub without relying on ffmpeg path
                try:
                    # First attempt - standard conversion
                    audio = AudioSegment.from_file(audio_file_path)
                    audio.export(temp_wav_path, format='wav')
                except Exception as pydub_error:
                    logger.warning(f"Standard conversion failed: {pydub_error}, trying raw conversion...")
                    # Second attempt - force raw conversion
                    try:
                        with open(audio_file_path, 'rb') as f:
                            audio_data = f.read()
                        
                        # Create a simple WAV file from raw PCM data
                        with wave.open(temp_wav_path, 'wb') as wav_file:
                            wav_file.setnchannels(1)  # Mono
                            wav_file.setsampwidth(2)  # 2 bytes (16 bits) per sample
                            wav_file.setframerate(16000)  # 16kHz sample rate
                            wav_file.writeframes(audio_data)
                        
                        logger.debug("Raw conversion completed")
                    except Exception as raw_error:
                        logger.error(f"Raw conversion failed: {raw_error}")
                        return "Error processing audio format. Please try again or type your response."
                
                logger.debug(f"Opening converted audio file for recognition: {temp_wav_path}")
                with sr.AudioFile(temp_wav_path) as source:
                    logger.debug("Recording audio data from file")
                    audio_data = self.recognizer.record(source)
                    
                    logger.debug("Sending audio to Google Speech Recognition")
                    text = self.recognizer.recognize_google(
                        audio_data,
                        language="en-US",
                        show_all=False
                    )
                    
                    logger.info(f"Transcription successful: '{text}'")
                    return text
                
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(temp_wav_path):
                        os.unlink(temp_wav_path)
                        logger.debug(f"Temporary file {temp_wav_path} deleted")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_wav_path}: {e}")
            
        except sr.UnknownValueError as e:
            logger.error(f"Google Speech Recognition could not understand audio: {e}")
            return "Could not understand audio. Please speak clearly and try again."
        except sr.RequestError as e:
            logger.error(f"Error with Google Speech Recognition service: {e}")
            return "Speech recognition service is currently unavailable. Please try again later or type your response."
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
            return "Error processing audio. Please try again or type your response."

# Initialize the SpeechToText instance
speech_to_text = SpeechToText()

def transcribe_audio(audio_path):
    """
    Transcribes audio file to text.
    
    Args:
        audio_path (str): Path to audio file
        
    Returns:
        str: Transcribed text
    """
    logger.debug(f"Starting transcription of audio file: {audio_path}")
    result = speech_to_text.convert_audio_to_text(audio_path)
    logger.debug(f"Transcription result: {result}")
    return result