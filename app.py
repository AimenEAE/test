import tkinter as tk
from tkinter import ttk, font
import threading
import logging
from stt import transcribe_audio
from tts import generate_speech
from gpt import get_chatbot_response
from loader import app_initializer

logging.basicConfig(level=logging.DEBUG)

class ChatbotApp:
    def __init__(self, master):
        self.master = master
        master.title("Voice-Enabled GPT-4 Chatbot")
        master.geometry("500x700")

        # Initialize the application
        self.initialize_app()

        # Set up fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=12, family="Segoe UI")
        chat_font = font.Font(family="Consolas", size=11)

        # Set up styles
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 12))

        self.chat_history = tk.Text(master, wrap=tk.WORD, state=tk.DISABLED, font=chat_font, bg="#F0F0F0")
        self.chat_history.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.button_frame = ttk.Frame(master)
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start Opname", command=self.toggle_recording)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.stop_button = ttk.Button(self.button_frame, text="Stop Opname", command=self.stop_and_process, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        self.is_recording = False
        self.conversation_history = []
        self.system_message_path = "system_message.txt"  # Path to your system message file
        self.stop_event = threading.Event()
        self.recording_thread = None

        # Set up text tags for coloring
        self.chat_history.tag_configure("you_tag", foreground="#0000FF", font=chat_font.copy().configure(weight="bold"))
        self.chat_history.tag_configure("chatbot_tag", foreground="#008000", font=chat_font.copy().configure(weight="bold"))

    def initialize_app(self):
        # Show a loading message
        loading_window = tk.Toplevel(self.master)
        loading_window.title("Loading")
        loading_label = tk.Label(loading_window, text="Initializing application...\nThis may take a moment.", font=("Segoe UI", 12))
        loading_label.pack(padx=20, pady=20)
        self.master.update()

        # Initialize the application
        app_initializer.initialize()

        # Close the loading window
        loading_window.destroy()

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_and_process()

    def start_recording(self):
        self.is_recording = True
        self.start_button.config(text="Recording...", state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_event.clear()
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
        self.update_chat_history("Openemen audio...", "system")
        logging.info("Recording started")

    def stop_and_process(self):
        if self.is_recording:
            self.is_recording = False
            self.start_button.config(text="Start Recording", state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.stop_event.set()
            if self.recording_thread:
                self.recording_thread.join()
            self.process_audio()
        logging.info("Recording stopped and processing started")

    def record_audio(self):
        try:
            self.audio_text = transcribe_audio(app_initializer.get_whisper_model(), self.stop_event)
        except Exception as e:
            logging.error(f"Error in record_audio: {e}")
            self.update_chat_history(f"Error recording audio: {e}", "system")

    def process_audio(self):
        self.update_chat_history("Audio verwerken...", "system")
        try:
            if hasattr(self, 'audio_text') and self.audio_text:
                self.update_chat_history(self.audio_text, "you")
                self.send_to_chatbot(self.audio_text)
            else:
                self.update_chat_history("No speech detected. Please try again.", "system")
        except Exception as e:
            logging.error(f"Error in process_audio: {e}")
            self.update_chat_history(f"Error processing audio: {e}", "system")

    def send_to_chatbot(self, user_message):
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})

            # Get response from GPT-4 based chatbot
            response = get_chatbot_response(user_message, self.system_message_path, self.conversation_history)
            self.update_chat_history(response, "chatbot")

            # Add chatbot response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})

            # Limit conversation history to last 10 messages to manage context length
            self.conversation_history = self.conversation_history[-10:]

            threading.Thread(target=self.speak_response, args=(response,)).start()
        except Exception as e:
            logging.error(f"Error in send_to_chatbot: {e}")
            self.update_chat_history(f"Error getting chatbot response: {e}", "system")

    def speak_response(self, text):
        try:
            generate_speech(text, app_initializer.get_elevenlabs_api_key(), app_initializer.get_elevenlabs_voice_id())
        except Exception as e:
            logging.error(f"Error in speak_response: {e}")
            self.update_chat_history(f"Error generating speech: {e}", "system")

    def update_chat_history(self, message, sender):
        self.chat_history.config(state=tk.NORMAL)
        if sender == "you":
            self.chat_history.insert(tk.END, "Jij: ", "you_tag")
            self.chat_history.insert(tk.END, message + "\n\n")
        elif sender == "chatbot":
            self.chat_history.insert(tk.END, "Chatbot: ", "chatbot_tag")
            self.chat_history.insert(tk.END, message + "\n\n")
        else:  # system messages
            self.chat_history.insert(tk.END, message + "\n\n", "system")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()