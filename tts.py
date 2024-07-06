import requests
import pygame
import os
from pydub import AudioSegment
import io
import tempfile


CHUNK_SIZE = 1024

def generate_speech(text, elevenlabs_api_key, elevenlabs_voice_id):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": False
        }
    }

    try:
        response = requests.post(tts_url, headers=headers, json=data, stream=True)
        if response.status_code == 200:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    temp_file.write(chunk)
            
            print("Audio stream saved successfully.")

            # Convert to WAV
            try:
                audio = AudioSegment.from_mp3(temp_path)
                wav_path = temp_path.replace(".mp3", ".wav")
                audio.export(wav_path, format="wav")
                print("Audio converted to WAV successfully.")

                # Play the audio
                play_audio(wav_path)

                # Clean up temporary files
                os.remove(temp_path)
                os.remove(wav_path)
            except Exception as e:
                print(f"Error converting or playing audio: {e}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error in generate_speech: {e}")

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
