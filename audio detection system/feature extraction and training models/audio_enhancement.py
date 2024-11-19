import os
import librosa
import soundfile as sf
import numpy as np
from scipy.signal import medfilt
from scipy.signal import butter, lfilter

#The enhancment functions :-
#applies spectral smoothing using a median filter
def spectral_smoothing(audio, sr):
    smoothed = medfilt(audio, kernel_size=5)
    return smoothed
#applies dynamic range compression
def dynamic_range_compression(audio):
    compressed = np.log1p(np.abs(audio)) * np.sign(audio)
    return compressed
#applies a high-pass filter
def apply_high_pass_filter(audio, sr, cutoff=100):
    b, a = butter(1, cutoff / (sr / 2), btype='high')
    filtered_audio = lfilter(b, a, audio)
    return filtered_audio
#normalize the audio to a range from -1 to 1
def normalize_audio(audio):
    return audio / np.max(np.abs(audio))

#combine functions
def enhancment(audio, sr):
    audio = spectral_smoothing(audio, sr)
    audio = dynamic_range_compression(audio)
    audio = apply_high_pass_filter(audio, sr)
    audio = normalize_audio(audio)
    return audio

# apply the enhancments on the input directory and output new directory
def enhance_and_save(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir) 
    for root, _, files in os.walk(input_dir):
        for file in files:
            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, input_dir)
            output_path = os.path.join(output_dir, relative_path)
            os.makedirs(output_path, exist_ok=True)
            try:
                audio, sr = librosa.load(input_path, sr=16000) 
                #enhance audio
                enhanced_audio = enhancment(audio, sr)
                #save
                output_file = os.path.join(output_path, file)
                sf.write(output_file, enhanced_audio, sr)
                print(f"saved: {output_file}")
            except Exception as e:
                print(f"Error processing {input_path}: {e}")

#define the dataset directories paths
train_fake_dir = "audio_dataset/release_in_the_wild/train/fake"
train_real_dir = "audio_dataset/release_in_the_wild/train/real"
val_fake_dir = "audio_dataset/release_in_the_wild/val/fake"
val_real_dir = "audio_dataset/release_in_the_wild/val/real"
test_fake_dir = "audio_dataset/release_in_the_wild/test/fake"
test_real_dir = "audio_dataset/release_in_the_wild/test/real"


#apply enhancment function to all directories
output_dir = "enhanced_audio"
enhance_and_save(train_fake_dir, os.path.join(output_dir, "train/fake"))
enhance_and_save(train_real_dir, os.path.join(output_dir, "train/real"))
enhance_and_save(val_fake_dir, os.path.join(output_dir, "val/fake"))
enhance_and_save(val_real_dir, os.path.join(output_dir, "val/real"))
enhance_and_save(test_fake_dir, os.path.join(output_dir, "test/fake"))
enhance_and_save(test_real_dir, os.path.join(output_dir, "test/real"))