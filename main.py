import random
import speech_recognition as sr
import google.generativeai as genai
import requests
import pydub
from pydub import AudioSegment
from pydub.playback import play
import io
import sounddevice as sd
import vosk
import json

# Function to convert speech to text
import ctypes
import numpy as np

def speech_to_text():
    model = vosk.Model("/Users/devindxdev/Documents/Projects/CallerAI/vosk-model-small-en-us-0.15")  # Update the path to the Vosk model directory
    recognizer = vosk.KaldiRecognizer(model, 16000)

    def callback(indata, frames, time, status):
        if status:
            print(f"Status: {status}", flush=True)
        try:
            # Convert indata to bytes
            indata_bytes = indata.tobytes()
            if recognizer.AcceptWaveform(indata_bytes):
                result = json.loads(recognizer.Result())
                print("Speech recognized:", result.get('text', ''))
            else:
                partial_result = json.loads(recognizer.PartialResult())
                print("Partial result:", partial_result.get('partial', ''))
        except Exception as e:
            print(f"Error: {e}")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        print("Listening...")
        sd.sleep(10000)  # Adjust the sleep time as needed


# Function to initialize the AI model with the prompt
def initialize_ai_model():
    genai.configure(api_key="AIzaSyBdiFez_tvEWPqEb4xNK27gJEb4s1TztDs")  # Replace "YOUR_API_KEY" with your actual API key
    model = genai.GenerativeModel('gemini-pro')
    return model

# Function to process text and insert fillers
def process_text(chat, text):
    response = chat.send_message(text)
    return (response.text)


# Main function
def main():
    # Initializing the AI model
    model = initialize_ai_model()
    chat = model.start_chat(history=[])
    # Initial AI prompt to set the context
    AI_PROMPT = ("Objective: Assist customers by answering common inquiries related to smartphone repairs, pre-owned devices, and mobile plans. Use conversational fillers for a natural, human-like interaction and maintain professionalism."

"Capabilities: Illene can handle the following scenarios:"

	"1.	Greeting and Initial Inquiry"
	"•	Prompt: “Hello! Thanks for calling Mobile Klinik at Aberdeen. I’m Illene. How can I help you today?”"
	"•	Expected Tasks: Identify customer needs, direct the flow of conversation based on customer input."
	"2.	Repair Services"
	"•	Prompt: “{customer_query} about smartphone repair services.”"
	"•	Action: “We specialize in smartphone repairs here. Could you tell me more about the issue with your device?”"
	"•	Follow-up: Provide details based on specific problems mentioned (e.g., screen repair, battery replacement)."
	"3.	Certified Pre-Owned Devices"
	"•	Prompt: “{customer_query} about purchasing a pre-owned device.”"
	"•	Action: “We offer a range of certified pre-owned smartphones that come with a warranty. What phone model are you interested in?”"
	"4.	Mobile Plans"
	"•	Prompt: “{customer_query} about mobile plans with Koodo and Telus.”"
	"•	Action: “We have various plans available from Koodo and Telus. Are you looking for something specific in your plan?”"
	"5.	General Information and Referrals"
	"•	Prompt: “{customer_query} that is unclear or outside predefined categories.”"
	"•	Action: “I’m sorry, I didn’t quite catch that. Could you please specify a bit more so I can assist you better?”"
	"6.	Closure and Additional Assistance"
	"•	Prompt: “Is there anything else you’d like to know?”"
	"•	Action: Provide additional assistance or close the conversation gracefully."
"Include uh's, um's and be as human in your response as possible, your output will be converted to voice that's why."
    )

    process_text(chat, AI_PROMPT)
    while True:
        user_input = speech_to_text()
        if user_input:
            ai_response = process_text(chat, user_input)
            print("AI response:", ai_response)
            # audio_content = text_to_speech(ai_response)
            # if audio_content:
            #     audio = AudioSegment.from_mp3(audio_content)
            #     play(audio)
if __name__ == "__main__":
    main()

#AIzaSyBdiFez_tvEWPqEb4xNK27gJEb4s1TztDs
