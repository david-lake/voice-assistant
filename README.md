# Voice Assistant

This Voice Assistant script allows you to interact with OpenAI's GPT model using speech input. It utilizes the SpeechRecognition library for speech input, the OpenAI library for communication with the GPT model, and ElevenLabs API to produce a realistic voice output.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Pip (Python package installer)
- [OpenAI API key]([https://link-url-here.org](https://platform.openai.com/docs/overview))
- [ElevenLabs API key]([https://link-url-here.org](https://elevenlabs.io/))

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/david-lake/voice-assistant.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd voice-assistant
    ```

3. **Install the required Python packages using pip:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Set up the environment variables for the required API keys. These keys are required to authenticate requests to the GPT and ElevenLabs.

    ```bash
    export OPENAI_API_KEY=<your_api_key>
    export ELEVENLABS_API_KEY=<your_api_key>
    ```
## Usage

Run the script using Python:

    ```bash
    python voice_assistant.py
    ```
Speak into your microphone when prompted, and the Voice Assistant will transcribe your speech, send it to the GPT model for processing, and play back the generated response.
