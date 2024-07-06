import os
import whisper
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AppInitializer:
    def __init__(self):
        self.whisper_model = None
        self.openai_api_key = None
        self.elevenlabs_api_key = None
        self.elevenlabs_voice_id = None

    def load_environment_variables(self):
        print("Loading environment variables...")
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.elevenlabs_api_key = os.getenv('XI_API_KEY')
        self.elevenlabs_voice_id = os.getenv('XI_VOICE_ID')

        if not all([self.openai_api_key, self.elevenlabs_api_key, self.elevenlabs_voice_id]):
            raise ValueError("Missing required environment variables. Please check your .env file.")

    def load_whisper_model(self, model_name="large-v2"):
        print(f"Loading Whisper model: {model_name}")
        self.whisper_model = whisper.load_model(model_name)

    def initialize(self):
        print("Initializing application...")
        self.load_environment_variables()
        self.load_whisper_model()
        print("Initialization complete.")

    def get_whisper_model(self):
        return self.whisper_model

    def get_elevenlabs_api_key(self):
        return self.elevenlabs_api_key

    def get_elevenlabs_voice_id(self):
        return self.elevenlabs_voice_id

# Create a global instance of the initializer
app_initializer = AppInitializer()