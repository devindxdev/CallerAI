# CallerAI

CallerAI is an advanced voice interaction system designed to handle customer phone calls efficiently, allowing staff to focus on other important tasks. The system leverages state-of-the-art speech recognition, generative AI, and text-to-speech technologies to provide a seamless, human-like conversational experience.

## Features

- **Voice Interaction**: Listens to customer queries and provides real-time responses.
- **AI-Driven Conversations**: Uses Google Generative AI for natural language understanding and response generation.
- **Text-to-Speech**: Converts AI responses into human-like speech using ElevenLabs API.
- **Speech Recognition**: Uses Vosk for accurate and efficient speech-to-text conversion.
- **Configurable**: Easy to set up and configure via a JSON file.

## Prerequisites

- Python 3.7 or higher
- Pip package manager

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/CallerAI.git
    cd CallerAI
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `config.json` file in the root directory with the following content:
    ```json
    {
        "google_api_key": "your_google_api_key",
        "elevenlabs_api_key": "your_elevenlabs_api_key",
        "elevenlabs_voice_id": "Iu3tg76F3g64V36OrFVV"
    }
    ```

2. Replace `"your_google_api_key"` and `"your_elevenlabs_api_key"` with your actual API keys.

## Usage

To run CallerAI, use the following command:
```sh
python caller_ai.py -c config.json
```

## How it works
 
- **Initialization:** Loads configuration settings and initializes the AI model with the provided API key.
- **Audio Input:** Captures audio input from the specified device.
- **Speech Recognition:** Converts the audio input to text using Vosk.
- **AI Processing:** Sends the recognized text to the AI model to generate a response.
- **Text-to-Speech:** Converts the AI response to speech using the ElevenLabs API and plays it back to the customer.
