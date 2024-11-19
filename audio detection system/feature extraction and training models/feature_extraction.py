import os
import librosa
import numpy as np
import pandas as pd
import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model
import parselmouth
import pywt


#wav2vec model
wav2vec_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
wav2vec_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
#function to extract the embeddings we need
def extract_wav2vec_embeddings(audio, sr):
    inputs = wav2vec_extractor(audio, sampling_rate=sr, return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = wav2vec_model(inputs.input_values).last_hidden_state
    return embeddings.mean(dim=1).squeeze().numpy()

#function to extract mfcc features we need
def extract_mfcc(audio, sr):
    return np.mean(librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13), axis=1)

#efunction for extracting audio formants
def extract_formants(audio, sr):
    sound = parselmouth.Sound(audio, sr)
    formant = sound.to_formant_burg()
    num_frames = formant.get_number_of_frames()
    f1, f2, f3 = [], [], []
    for i in range(num_frames):
        t = formant.get_time_from_frame_number(i + 1)
        f1_val = formant.get_value_at_time(1, t)
        f2_val = formant.get_value_at_time(2, t)
        f3_val = formant.get_value_at_time(3, t)
        if f1_val is not None:
            f1.append(f1_val)
        if f2_val is not None:
            f2.append(f2_val)
        if f3_val is not None:
            f3.append(f3_val)
    return [np.mean(f1), np.mean(f2), np.mean(f3)]
#function to extract harmonics-to-noise ratio 
def extract_hnr(audio, sr):
    sound = parselmouth.Sound(audio, sr)
    hnr = sound.to_harmonicity()
    hnr_values = hnr.values if hnr.values.size > 0 else [0]  # Handle empty hnr values
    return np.mean(hnr_values)

#function to extract pause analysis
def extract_pause_analysis(audio, sr):
    intervals = librosa.effects.split(audio, top_db=30)
    total_speech = np.sum([interval[1] - interval[0] for interval in intervals]) / sr
    total_duration = len(audio) / sr
    pause_ratio = (total_duration - total_speech) / total_duration
    return [total_speech, pause_ratio]

#function to extract wavlets
def extract_wavelets(audio):
    coeffs = pywt.wavedec(audio, 'db1', level=5)
    wavelet_features = np.hstack([np.mean(c) for c in coeffs] + [np.std(c) for c in coeffs])
    return wavelet_features
#function to extract psychoacoustic features
def extract_psychoacoustic(audio, sr):
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sr))
    spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=audio, sr=sr))
    return [spectral_centroid, spectral_bandwidth, spectral_contrast]

#extract all the features we need and save them to csv file
def extract_features(input_dir, output_file):
    data = []
    print(f"Processing directory: {input_dir}")
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".wav"):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")
                try:
                    audio, sr = librosa.load(file_path, sr=16000)
                    features = {
                        "file_path": file_path,
                        "wav2vec_embeddings": extract_wav2vec_embeddings(audio, sr).tolist(),
                        "mfcc": extract_mfcc(audio, sr).tolist(),
                        "formants": extract_formants(audio, sr),
                        "hnr": extract_hnr(audio, sr),
                        "pause_analysis": extract_pause_analysis(audio, sr),
                        "wavelets": extract_wavelets(audio).tolist(),
                        "psychoacoustic": extract_psychoacoustic(audio, sr),
                    }
                    data.append(features)
                    print(f"Successfully processed {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
   
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        
#apply to the newly enhanced audio directories
if __name__ == "__main__":
    extract_features("enhanced_audio/train/fake", "features_fake_train.csv")
    extract_features("enhanced_audio/train/real", "features_real_train.csv")
    extract_features("enhanced_audio/val/fake", "features_fake_val.csv")
    extract_features("enhanced_audio/val/real", "features_real_val.csv")
    extract_features("enhanced_audio/test/fake", "features_fake_test.csv")
    extract_features("enhanced_audio/test/real", "features_real_test.csv")
