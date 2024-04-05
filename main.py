#!/usr/bin/env python3

import os
import sys
import speech_recognition as sr
from openai import OpenAI
import requests
from playsound import playsound

recognizer = sr.Recognizer()
client = OpenAI()
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')

# Check if the environment variable exists
if ELEVENLABS_API_KEY is  None:
  print("ELEVENLABS_API_KEY is not set")
  sys.exit(1)

CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": ELEVENLABS_API_KEY
}

prompt = None
    
# obtain audio from the microphone
with sr.Microphone() as source:
    print("Listening...")
    audio = recognizer.listen(source)

try:
    print("Recognizing...")
    prompt = recognizer.recognize_google(audio)
except sr.UnknownValueError:
    print("Sorry, I didn't understand that.")
except sr.RequestError:
    print("Sorry, there was an issue with the speech recognition service.")

if prompt != None:
    print(prompt)
    
    # send response to GPT
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
          {"role": "user", "content": prompt}
      ]
    )

    # Play response
    print(completion.choices[0].message.content)

    data = {
      "text": completion.choices[0].message.content,
      "model_id": "eleven_monolingual_v1",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
      }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
      for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
          if chunk:
              f.write(chunk)

    playsound("output.mp3")
    prompt = None