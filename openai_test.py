# import os
# import openai
import whisper
# import nltk
# import pydub
import json

# openai.organization = "org-objxRwpXBA7Ncmmg7daB5QiU"
# openai.api_key = "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"

# prompt='Say this is a test'
# response=openai.Completion.create(
#   engine="text-davinci-001",
#   prompt=prompt,
#   max_tokens=6,
#   temperature=0.3,
#   stop="\n\n")


# print(response)


# Load a model
model = whisper.load_model("base")

# Read an mp3 file and convert it to wav format
# sound = pydub.AudioSegment.from_mp3("audio.wav")
# sound.export("audio.wav", format="wav")

# Transcribe the wav file
model = whisper.load_model("base")
audio = whisper.load_audio("audio2.mp3")
result = model.transcribe(audio=audio)

# Split the text into sentences
outputs = []

# Initialize a list for JSON output

# Initialize a variable for start time
start = 0

for segment in result["segments"]:
  outputs.append({
    "text": segment["text"],
    "from": segment["start"],
    "to": segment["end"]
  })
json_output = json.dumps(outputs)


    # Append the dictionary to the sentences list

# Convert the sentences list to a JSON format

# Print the output as JSON string
print(json_output)

