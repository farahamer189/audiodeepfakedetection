from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model
import librosa
import numpy as np
import torch

# Load the feature extractor and Wav2Vec model
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")

def extract_wav2vec_embeddings(audio_path):
    # Load the audio file and resample to 16kHz
    audio, sr = librosa.load(audio_path, sr=16000)
    # Use the feature extractor to preprocess the audio
    inputs = feature_extractor(audio, sampling_rate=sr, return_tensors="pt", padding=True)
    with torch.no_grad():
        # Get the embeddings from the model
        embeddings = model(inputs.input_values).last_hidden_state
    # Return the averaged embedding vector (single fixed-size vector)
    return embeddings.mean(dim=1).squeeze().numpy()

def extract_combined_features(audio_path):
    # Extract Wav2Vec embeddings
    wav2vec_embeddings = extract_wav2vec_embeddings(audio_path)
    # Add optional traditional features like MFCC
    audio, sr = librosa.load(audio_path, sr=16000)
    mfcc = np.mean(librosa.feature.mfcc(y=audio, sr=sr), axis=1)
    # Combine embeddings and MFCC features into one vector
    combined_features = np.hstack((wav2vec_embeddings, mfcc))
    return combined_features
