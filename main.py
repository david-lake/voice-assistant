#!/usr/bin/env python3

import os
import sys
import asyncio
import websockets
import json
import base64
import shutil
import subprocess
from openai import AsyncOpenAI
import speech_recognition as sr

# Define API keys and voice ID
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
VOICE_ID = '21m00Tcm4TlvDq8ikWAM'

# Check for presents of Open AI API key
if OPENAI_API_KEY is  None:
  print("OPENAI_API_KEY is not set")
  sys.exit(1)

# Check for presents of Eleven Labs API key
if ELEVENLABS_API_KEY is  None:
  print("ELEVENLABS_API_KEY is not set")
  sys.exit(1)

# Set OpenAI API key
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)
recognizer = sr.Recognizer()
prompt = None

def is_installed(lib_name):
    return shutil.which(lib_name) is not None

async def text_chunker(chunks):
    # Split text into chunks, ensuring to not break sentences.
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if buffer.endswith(splitters) and text is not None:
            yield buffer + " "
            buffer = text
        if text is not None and text.startswith(splitters):
            yield buffer + text[0] + " "
            buffer = text[1:]
        else:
            buffer += text if text is not None else ""  # Avoid None concatenation

    if buffer:
        yield buffer + " "

async def stream(audio_stream):
    # Stream audio data using mpv player.
    print(audio_stream)
    if not is_installed("mpv"):
        raise ValueError(
            "mpv not found, necessary to stream audio. "
            "Install instructions: https://mpv.io/installation/"
        )

    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    print("Started streaming audio")
    async for chunk in audio_stream:
        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()

async def text_to_speech_input_streaming(voice_id, text_iterator):
    # Send text to ElevenLabs API and stream the returned audio.
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_monolingual_v1"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
            "xi_api_key": ELEVENLABS_API_KEY,
        }))

        async def listen():
            """Listen to the websocket for audio data and stream it."""
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get('isFinal'):
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

        listen_task = asyncio.create_task(stream(listen()))

        async for text in text_chunker(text_iterator):
            await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))

        await websocket.send(json.dumps({"text": ""}))

        await listen_task

async def chat_completion(query):
    # Retrieve text from OpenAI and pass it to the text-to-speech function.
    response = await aclient.chat.completions.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': query}],
    temperature=1, stream=True)

    async def text_iterator():
        async for chunk in response:
            delta = chunk.choices[0].delta
            yield delta.content

    await text_to_speech_input_streaming(VOICE_ID, text_iterator())

# Main execution
if __name__ == "__main__":
    while(1):
      # obtain audio from the microphone
      with sr.Microphone() as source:
          print("Listening...")
          audio = recognizer.listen(source, phrase_time_limit=5)

      try:
          print("Recognizing...")
          prompt = recognizer.recognize_google(audio)
      except sr.UnknownValueError:
          print("Sorry, I didn't understand that.")
      except sr.RequestError:
          print("Sorry, there was an issue with the speech recognition service.")

      if prompt != None:
        print(prompt)
        asyncio.run(chat_completion(prompt))
        prompt = None