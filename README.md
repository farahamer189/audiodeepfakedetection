Deepfake Voice Detection and Audio Enhancement System
Project Overview
Our program main function is to detect deepfake synthetic audio from authentic real human audio,while also enhancing the quality of audio recordings.Our final product is a web application that lets users upload any audio file containing speech, and our system will preprocess and analyze the audio, giving the user a simple result whether the voice in the audio is real or deepfake .

Firstly, The system makes the following audio enhancments before extracting the features :-
-Noise Removal
-Spectral Smoothing
-Dynamic Range Compression
-Volume Normalization

Secondly, the system extracts the following features from the audio: -
-Wav2Vec embeddings
-MFCC (Mel Frequency Cepstral Coefficients)
-Formants
-HNR (Harmonics-to-Noise Ratio)
-Pause Analysis
-Wavelets
-Psychoacoustic features

finally, the system tests(inference) the features with our trained FCNN model and returns the result.


Libraries used :
Transformers, Librosa, NumPy, Pandas, Matplotlib, Seaborn, PyTorch, scikit-learn.
Deep Learning Frameworks: PyTorch for building and training the FCNN model.


Directory :
├── old files                 # old versions and testing algorithms (original files)

├── audio detection system    # final system

├── README.md                 # Project documentation
