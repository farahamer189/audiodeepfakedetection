from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import os
from datetime import datetime
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import noisereduce as nr  # Import the noise reduction library
from scipy.signal import resample
import random
import time
import wave
import speech_recognition as sr

app = Flask(__name__)

# Initialize the camera
camera = cv2.VideoCapture(0)

# Load the face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Global variables
client_folder = ''
step = 1  # Step tracker

@app.route('/')
def index():
    return render_template('index.html', step=step)

@app.route('/next_step', methods=['POST'])
def next_step():
    global step, client_folder

    if step == 1:  # Step 1: Get the user's name
        name = request.form['name']
        client_folder = f"clients/{name}"
        
        if not os.path.exists(client_folder):  # Create folder named after the client
            os.makedirs(client_folder)

        step = 2  # Move to step 2
        return redirect(url_for('index'))

    elif step == 2:  # Step 2: Face recognition and save image
        save_face_image(client_folder)  # Save the detected face image
        step = 3  # Move to step 3
        return redirect(url_for('index'))

    elif step == 3:  # Step 3: Start recording the voice
        record_voice(client_folder)
        step = 4  # Move to step 4
        return redirect(url_for('index'))

    else:
        return "Error."

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Encode the frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def save_face_image(folder):
    # Capture a frame and save the face image
    success, frame = camera.read()
    if success:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]  # Crop the face
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                face_filename = os.path.join(folder, f"face_{timestamp}.jpg")
                cv2.imwrite(face_filename, face)  # Save the face image
                print(f"Face saved to: {face_filename}")
        else:
            print("No face detected.")
    else:
        print("Failed to capture a frame.")

def record_voice(folder):
    fs = 22050  # Reduced sample rate (down from 44100 Hz to 22050 Hz)
    duration = 1  # Duration in seconds (try to keep this as small as possible)

    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is done
    print("Recording complete!")

    # Downsample the recording to reduce memory usage
    downsample_factor = 4  # Reduce sample rate to one-fourth (downsampling)
    new_fs = fs // downsample_factor
    downsampled_recording = resample(recording, int(len(recording) / downsample_factor), axis=0)

    # Process the audio in smaller chunks (e.g., 0.5-second chunks)
    chunk_size = new_fs // 2  # 0.5 second of audio (downsampled)
    processed_audio = []

    # Split the downsampled audio into chunks and process each chunk
    num_chunks = len(downsampled_recording) // chunk_size
    for i in range(num_chunks):
        chunk = downsampled_recording[i * chunk_size:(i + 1) * chunk_size]
        reduced_chunk = nr.reduce_noise(y=chunk, sr=new_fs)  # Apply noise reduction to each chunk
        processed_audio.append(reduced_chunk)

    # Concatenate the processed chunks
    reduced_noise = np.concatenate(processed_audio, axis=0)

    # Save the processed (denoised) audio to the client's folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_path = os.path.join(folder, f"voice_{timestamp}.wav")

    # Use scipy to save the wav file
    wav.write(new_path, new_fs, reduced_noise)

    print(f"Voice saved to: {new_path}")

def generate_random_word():
    words = ["apple", "banana", "carrot", "dog", "elephant"]
    return random.choice(words)

def voice_match(client_folder):
    # Record the voice
    fs = 22050  # Reduced sample rate (down from 44100 Hz to 22050 Hz)
    duration = 2  # Duration in seconds

    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is done
    print("Recording complete!")

    # Load saved voice file and compare with new recording
    saved_voice_path = os.path.join(client_folder, "voice_20231207_123456.wav")
    saved_fs, saved_voice = wav.read(saved_voice_path)

    # Apply noise reduction to the recorded voice
    reduced_recording = nr.reduce_noise(y=recording, sr=fs)
    reduced_saved_voice = nr.reduce_noise(y=saved_voice, sr=saved_fs)

    # Compare the voices (simple matching logic for now)
    if np.array_equal(reduced_recording, reduced_saved_voice):
        print("Voice match successful! Door opens.")
    else:
        print("Voice does not match.")

if __name__ == '__main__':
    app.run(debug=True)
