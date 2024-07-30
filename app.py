import gradio as gr
import torch
from transformers import pipeline
import soundfile as sf
import librosa
import numpy as np
from TTS.api import TTS
import os
os.environ["COQUI_TOS_AGREED"] = "1"    

# Check if CUDA is available and set the device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize models
asr_model = pipeline("automatic-speech-recognition", model="jonatasgrosman/wav2vec2-large-xlsr-53-spanish", device=device)
translation_model = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en", device=device)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

def process_audio(input_file):
    # Load audio
    speech, sr = librosa.load(input_file)

    # Perform ASR
    transcription = asr_model(speech)["text"]
    print(f"Spanish transcription: {transcription}")

    # Translate
    translation = translation_model(transcription)[0]["translation_text"]
    print(f"English translation: {translation}")

    # Define output file path
    output_file = "output_audio.mp3"
    
    # Voice cloning and TTS
    tts.tts_to_file(
        text=translation,
        speaker_wav=input_file,
        language="en",
        file_path=output_file
    )

    print(f"Output saved to: {output_file}")
    return transcription, translation, output_file

# Define the Gradio interface
inputs = gr.Audio(type="filepath")
outputs = [gr.Textbox(label="Transcripción en Español 🇪🇸"), 
           gr.Textbox(label="Traducción al Inglés 🇺🇸"),
           gr.Audio(type="filepath", label="Audio Traducido")]

# Define example inputs
examples = [
    ["./examples/erizo.mp3"],
    ["./examples/quimica.mp3"]
]

gr_interface = gr.Interface(
    fn=process_audio,
    inputs=inputs,
    outputs=outputs,
    examples=examples,
    title="Transformación de Voz en Español a Inglés 📢",
    description=(
        "Modelos utilizados:\n"
        "- **Reconocimiento Automático del Habla (ASR)**: `jonatasgrosman/wav2vec2-large-xlsr-53-spanish` \n"
        "- **Traducción de Español a Inglés**: `Helsinki-NLP/opus-mt-es-en` \n"
        "- **Síntesis de Voz (TTS)**: `tts_models/multilingual/multi-dataset/xtts_v2` (Uso no comercial) \n\n"
        "Dani Servian, 2024"
    ),
    allow_flagging="never"
)

# Launch the Gradio interface
if __name__ == "__main__":
    gr_interface.launch()
