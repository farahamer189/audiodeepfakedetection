from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch
import librosa
import os

# Load the pre-trained model and feature extractor
model = AutoModelForAudioClassification.from_pretrained("./")
feature_extractor = AutoFeatureExtractor.from_pretrained("./")

# Set model to evaluation mode
model.eval()


# Prompt the user to enter the folder path for audio files
audio_folder = input("Please enter the folder path containing the audio files: ")

# Check if the folder exists
if not os.path.isdir(audio_folder):
    print(f"Error: The folder '{audio_folder}' does not exist.")
else:
    # Check if the folder contains any files
    files = os.listdir(audio_folder)
    if not files:
        print(f"Error: No files found in the folder '{audio_folder}'.")
    else:
        # Loop through each file in the folder
        for file_name in files:
            print(f"Checking file: {file_name}")
            if file_name.endswith((".mp3", ".wav")):  # Check for mp3 and wav files
                file_path = os.path.join(audio_folder, file_name)
                print(f"Processing file: {file_name}")

                try:
                    # Load the mp3 or wav file and resample to 16kHz
                    audio, sample_rate = librosa.load(file_path, sr=16000)  # Resample to 16000 Hz
                    print(f"Audio loaded: {file_name}")

                    # Extract features from the audio
                    inputs = feature_extractor(audio, sampling_rate=16000, return_tensors="pt")  # Use 16000 as the sampling rate
                    print(f"Features extracted for: {file_name}")

                    # Perform inference
                    with torch.no_grad():
                        logits = model(**inputs).logits
                    print(f"Inference completed for: {file_name}")

                    # Get the predicted class
                    predicted_class = torch.argmax(logits, dim=-1).item()
                    print(f"File: {file_name}, Predicted class: {predicted_class}")
                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")
            else:
                print(f"Skipping non-audio file: {file_name}")
