import pyaudio
import wave
import threading
import os
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG)

def record_audio(filename, sample_rate=16000, channels=1, stop_event=None):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)

    logging.info("Recording started...")
    frames = []
    
    while not stop_event.is_set():
        data = stream.read(1024)
        frames.append(data)
        
    logging.info("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    logging.info(f"Audio saved to {filename}")
    return filename

def transcribe_audio(whisper_model, stop_event):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        record_audio(temp_filename, stop_event=stop_event)
        
        logging.info("Transcribing audio...")
        result = whisper_model.transcribe(temp_filename, fp16=False)
        transcribed_text = result["text"]
        logging.info(f"Transcription result: {transcribed_text}")
        
        return transcribed_text
    except Exception as e:
        logging.error(f"Error in transcribe_audio: {e}")
        return "Error transcribing audio. Please try again."
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            logging.info(f"Temporary file {temp_filename} removed.")