import os
import librosa
import numpy as np
import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model
import pandas as pd

# Load Wav2Vec model and move to GPU
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h").to("cuda")
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")

def extract_wav2vec_embeddings(audio_path):
    """
    Extract Wav2Vec embeddings from a given audio file.

    Parameters:
        audio_path (str): Path to the audio file.

    Returns:
        numpy.ndarray: Fixed-size embedding vector (1D).
    """
    audio, sr = librosa.load(audio_path, sr=16000)
    
    # Skip empty or short audio
    if len(audio) < 1600:  # Minimum length: 100ms at 16kHz
        raise ValueError(f"Audio file too short: {audio_path}")
    
    inputs = feature_extractor(audio, sampling_rate=sr, return_tensors="pt", padding=True)
    inputs.input_values = inputs.input_values.to("cuda")
    
    with torch.no_grad():
        embeddings = model(inputs.input_values).last_hidden_state
    return embeddings.mean(dim=1).cpu().numpy().squeeze()  # Ensure 1D

def extract_mfcc_features(audio_path, n_mfcc=20):
    """
    Extract MFCC features from a given audio file.

    Parameters:
        audio_path (str): Path to the audio file.
        n_mfcc (int): Number of MFCC coefficients to extract.

    Returns:
        numpy.ndarray: MFCC feature vector (1D).
    """
    audio, sr = librosa.load(audio_path, sr=16000)
    
    # Skip empty or short audio
    if len(audio) < 1600:
        raise ValueError(f"Audio file too short: {audio_path}")
    
    mfcc = np.mean(librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc, n_fft=min(len(audio), 2048)).T, axis=0)
    return mfcc

def preprocess_audio_dataset(real_dir, fake_dir, output_csv="dataset.csv"):
    """
    Preprocess the audio dataset by extracting features (Wav2Vec + MFCC) and saving them to a CSV.

    Parameters:
        real_dir (str): Path to the directory containing real audio files.
        fake_dir (str): Path to the directory containing fake audio files.
        output_csv (str): Path to the output CSV file.
    """
    data = []
    real_files = os.listdir(real_dir)
    fake_files = os.listdir(fake_dir)

    # Take only half of the real files
    real_files = real_files[:len(real_files) // 2]

    for label, (directory, file_list) in enumerate([(real_dir, real_files), (fake_dir, fake_files)]):
        for filename in file_list:
            if filename.endswith(".wav"):
                filepath = os.path.join(directory, filename)
                try:
                    # Extract Wav2Vec and MFCC features
                    wav2vec_embeddings = extract_wav2vec_embeddings(filepath)
                    mfcc_features = extract_mfcc_features(filepath)
                    
                    # Combine features
                    combined_features = np.hstack((wav2vec_embeddings, mfcc_features))
                    
                    # Append features and label
                    data.append(list(combined_features) + [label])
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    # Save dataset to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False, header=False)
    print(f"Preprocessing complete. Data saved to {output_csv}.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Preprocess audio dataset")
    parser.add_argument("--real_dir", type=str, required=True, help="Path to real audio files")
    parser.add_argument("--fake_dir", type=str, required=True, help="Path to fake audio files")
    parser.add_argument("--output_csv", type=str, default="dataset.csv", help="Path to output CSV file")
    args = parser.parse_args()
    preprocess_audio_dataset(args.real_dir, args.fake_dir, args.output_csv)
