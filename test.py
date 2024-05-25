import json
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import requests
import argparse
import queue
import sys
import sounddevice as sd
import google.generativeai as genai
import io
import threading
from vosk import Model, KaldiRecognizer

# Global queue and event
q = queue.Queue()
tts_playing_event = threading.Event()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    if not tts_playing_event.is_set():
        q.put(bytes(indata))

def load_config(config_file):
    """Load configuration settings from a JSON file."""
    with open(config_file, 'r') as file:
        return json.load(file)

def initialize_ai_model(api_key):
    """Initializes the AI model with the provided API key."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest',
        system_instruction=(
            "You are Luna, an assistant to take phone calls from customers for <REDACTED> "
            "Your job is to greet customers, understand their needs, provide troubleshooting help if possible, and offer information about additional services, "
            "especially mobile plans with <REDACTED>. When encountering situations where immediate assistance isn’t possible, you will pass the call to the senior team. "
            "Keep your responses casual and human-like, including natural speech patterns and pauses. Now you are ready to take calls. Keep responses short and sweet."
        )
    )
    return model

def process_text(chat, text):
    """Processes the text using the AI model and returns the response."""
    response = chat.send_message(text)
    return response.text

def text_to_speech(text, api_key, voice_id):
    """Converts text to speech using the ElevenLabs API."""
    tts_playing_event.set()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.30,
            "similarity_boost": 0.75,
            "style": 1.0,
            "use_speaker_boost": True
        }
    }
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        audio_content = response.content
        audio = AudioSegment.from_file(io.BytesIO(audio_content))
        play(audio)
    else:
        print(f"Failed to generate speech: {response.status_code} - {response.text}")
    tts_playing_event.clear()

def main():
    parser = argparse.ArgumentParser(description="Voice Interaction AI")
    parser.add_argument("-c", "--config", type=str, default="config.json", help="Path to the config file")
    parser.add_argument("-f", "--filename", type=str, metavar="FILENAME", help="Audio file to store recording to")
    parser.add_argument("-d", "--device", type=int_or_str, help="Input device (numeric ID or substring)")
    parser.add_argument("-r", "--samplerate", type=int, help="Sampling rate")
    parser.add_argument("-m", "--model", type=str, help="Language model; e.g. en-us, fr, nl; default is en-us")
    parser.add_argument("-l", "--list-devices", action="store_true", help="Show list of audio devices and exit")
    args = parser.parse_args()
#Gradio - python to UI
    if args.list_devices:
        print(sd.query_devices())
        sys.exit(0)

    # Load configuration
    config = load_config(args.config)
    google_api_key = config["google_api_key"]
    elevenlabs_api_key = config["elevenlabs_api_key"]
    elevenlabs_voice_id = config.get("elevenlabs_voice_id", "Iu3tg76F3g64V36OrFVV")

    # Initialize the AI model
    model = initialize_ai_model(google_api_key)
    chat = model.start_chat(history=[])

    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, "input")
            args.samplerate = int(device_info["default_samplerate"])
        
        if args.model is None:
            vosk_model = Model(lang="en-us")
        else:
            vosk_model = Model(lang=args.model)

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None
        
        with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device, dtype="int16", channels=1, callback=callback):
            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print("#" * 80)

            rec = KaldiRecognizer(vosk_model, args.samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result_string = rec.Result()
                    print(result_string)
                    try:
                        result_dict = json.loads(result_string)
                    except json.JSONDecodeError:
                        result_dict = {}
                    text_data = result_dict.get("text", "")
                    if text_data!="":
                        print("Speech Text:", text_data)
                        ai_response = process_text(chat, text_data)
                        print("AI response:", ai_response)
                        text_to_speech(ai_response, elevenlabs_api_key, elevenlabs_voice_id)
                if dump_fn is not None:
                    dump_fn.write(data)

    except KeyboardInterrupt:
        print("\nDone")
        sys.exit(0)
    except Exception as e:
        sys.exit(f"{type(e).__name__}: {e}")
    finally:
        if dump_fn:
            dump_fn.close()

if __name__ == "__main__":
    main()
