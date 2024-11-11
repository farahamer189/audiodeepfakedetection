import joblib
import numpy as np
import torch
import librosa
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model

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
    
    if len(audio) < 1600:  # Skip very short audio files
        raise ValueError("Audio file too short for processing.")
    
    inputs = feature_extractor(audio, sampling_rate=sr, return_tensors="pt", padding=True)
    inputs.input_values = inputs.input_values.to("cuda")  # Move input to GPU
    
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
    mfcc = np.mean(librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc, n_fft=min(len(audio), 2048)).T, axis=0)
    return mfcc

def predict(audio_path, model_path="classifier.pkl"):
    """
    Predict whether an audio file is real or fake using the trained classifier.

    Parameters:
        audio_path (str): Path to the audio file.
        model_path (str): Path to the trained classifier file.

    Returns:
        str: "Real" or "Fake" depending on the classifier's prediction.
    """
    # Load the trained classifier
    clf = joblib.load(model_path)

    # Extract features
    wav2vec_embeddings = extract_wav2vec_embeddings(audio_path)
    mfcc_features = extract_mfcc_features(audio_path)
    combined_features = np.hstack((wav2vec_embeddings, mfcc_features))

    # Make prediction
    prediction = clf.predict([combined_features])[0]
    return "Real" if prediction == 1 else "Fake"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run inference on a single audio file")
    parser.add_argument("--audio_path", type=str, required=True, help="Path to the audio file")
    parser.add_argument("--model_path", type=str, default="classifier.pkl", help="Path to the trained classifier")
    args = parser.parse_args()

    try:
        result = predict(args.audio_path, args.model_path)
        print(f"The audio is predicted to be: {result}")
    except Exception as e:
        print(f"Error during inference: {e}")
