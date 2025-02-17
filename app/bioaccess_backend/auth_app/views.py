import os
import tempfile
import difflib
import random
import requests
import cv2
import torch
import torchaudio

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Room, AccessLog, DeniedLog, RoomGroup
from .serializers import UserSerializer, AccessLogSerializer, DeniedLogSerializer, RoomSerializer
from deepface import DeepFace

# ------------------ Speaker Verification using Resemblyzer ------------------
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.spatial.distance import cosine

# Initialize the Resemblyzer VoiceEncoder (pre-trained model)
encoder = VoiceEncoder()

def verify_speaker(audio_path, reference_voice_path):
    """
    Uses Resemblyzer to compare the speaker in the provided audio sample with the stored reference.
    Returns a tuple (verified: bool, similarity: float) where similarity is in [0, 1].
    """
    try:
        wav_current = preprocess_wav(audio_path)
        wav_reference = preprocess_wav(reference_voice_path)
        
        embedding_current = encoder.embed_utterance(wav_current)
        embedding_reference = encoder.embed_utterance(wav_reference)
        
        similarity = 1 - cosine(embedding_current, embedding_reference)
        print("Speaker similarity score:", similarity)
        threshold = 0.73  # Threshold set to 0.73
        return (similarity > threshold, similarity)
    except Exception as e:
        print("Speaker verification error:", e)
        return (False, 0.0)

# ------------------ Deepfake Detection using Hugging Face Model ------------------
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

# Load the deepfake detection model (assume: genuine audio is predicted with class 1)
deepfake_feature_extractor = AutoFeatureExtractor.from_pretrained("MelodyMachine/Deepfake-audio-detection-V2")
deepfake_model = AutoModelForAudioClassification.from_pretrained("MelodyMachine/Deepfake-audio-detection-V2")

def detect_deepfake(audio_path):
    """
    Loads the audio file using torchaudio, resamples it to 16000 Hz if necessary,
    and processes it through the deepfake feature extractor and model.
    Returns True if the predicted class is 1 (genuine audio).
    """
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)
        sample_rate = 16000
    inputs = deepfake_feature_extractor(waveform.squeeze(), sampling_rate=sample_rate, return_tensors="pt")
    outputs = deepfake_model(**inputs)
    logits = outputs.logits
    predicted_class = logits.argmax(dim=-1).item()
    print("Deepfake predicted class:", predicted_class)
    return predicted_class == 1

# ------------------ Helper Function for Face Verification ------------------
def verify_face(uploaded_face_image, reference_image_path):
    """
    Saves the uploaded face image to a temporary file and uses DeepFace (VGG-Face)
    to compare it with the stored reference image.
    Returns True if the face is verified, else False.
    """
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        for chunk in uploaded_face_image.chunks():
            temp_file.write(chunk)
        temp_path = temp_file.name
    try:
        result = DeepFace.verify(
            img1_path=temp_path,
            img2_path=reference_image_path,
            model_name="VGG-Face",
            enforce_detection=False
        )
        verified = result.get('verified', False)
    except Exception as e:
        print("DeepFace verification error:", e)
        verified = False
    finally:
        try:
            os.remove(temp_path)
        except Exception as e:
            print("Error deleting temp file:", e)
    return verified

# ------------------ User Registration and Login Endpoints ------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    is_admin = request.data.get('is_admin', False)
    face_reference_image = request.FILES.get('face_reference_image')
    voice_reference = request.FILES.get('voice_reference')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = CustomUser.objects.create(
        username=username,
        email=email,
        is_admin=is_admin,
        password=make_password(password),
        face_reference_image=face_reference_image,
        voice_reference=voice_reference,
    )
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            # Optionally include role information if needed.
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ------------------ Biometric Authentication Endpoints ------------------

## Face Authentication Endpoint
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def face_auth(request):
    """
    Receives room_id and a captured face_image.
    Uses DeepFace (VGG-Face) to verify the face against the stored reference image.
    Returns a challenge sentence for voice authentication if successful.
    """
    user = request.user
    room_id = request.data.get('room_id')
    face_image = request.FILES.get('face_image')
    
    if not room_id or not face_image:
        return Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        room = Room.objects.get(room_id=room_id)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if room.group not in user.allowed_room_groups.all():
        DeniedLog.objects.create(user=user, room=room, reason="User not permitted for this room.")
        return Response({'error': 'User does not have permission for this room'}, status=status.HTTP_403_FORBIDDEN)
    
    if not user.face_reference_image:
        DeniedLog.objects.create(user=user, room=room, reason="No face reference image found.")
        return Response({'error': 'No face reference image found. Please enroll your face.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not verify_face(face_image, user.face_reference_image.path):
        DeniedLog.objects.create(user=user, room=room, reason="Face verification failed.")
        return Response({'message': 'Face verification failed'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        resp = requests.get("https://api.quotable.io/random", verify=False)
        if resp.status_code == 200:
            data = resp.json()
            sentence = data.get("content", "Please say the following sentence.")
        else:
            sentence = "Please say the following sentence."
    except Exception as e:
        print("Random sentence API error:", e)
        sentence = "Please say the following sentence."
    
    return Response({'face_verification': True, 'challenge_sentence': sentence})

## Voice Authentication Endpoint
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_auth(request):
    """
    Receives room_id, expected_sentence, and an audio_sample.
    Converts the audio_sample to WAV using pydub.
    Transcribes the audio using SpeechRecognition.
    Performs speaker verification using Resemblyzer.
    Runs deepfake detection using the Hugging Face model.
    Uses fuzzy matching (>=80% similarity) between the transcription and expected_sentence.
    Rounds the transcription and speaker similarity scores to whole percentages.
    Logs the result in AccessLog if successful or in DeniedLog if failed.
    """
    user = request.user
    room_id = request.data.get('room_id')
    expected_sentence = request.data.get('expected_sentence')
    audio_sample = request.FILES.get('audio_sample')
    
    if not room_id or not expected_sentence or not audio_sample:
        return Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        room = Room.objects.get(room_id=room_id)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        import speech_recognition as sr
    except ModuleNotFoundError:
        return Response({'error': 'SpeechRecognition module not installed. Install via "pip install SpeechRecognition".'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    recognizer = sr.Recognizer()
    
    # Save the uploaded audio sample to a temporary file.
    try:
        original_suffix = os.path.splitext(audio_sample.name)[1] or ".webm"
        tmp_audio_file = tempfile.NamedTemporaryFile(suffix=original_suffix, delete=False)
        for chunk in audio_sample.chunks():
            tmp_audio_file.write(chunk)
        tmp_audio_file.close()
        tmp_audio_path = tmp_audio_file.name
    except Exception as e:
        return Response({'error': f"Failed to save audio file: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Convert the audio sample to WAV using pydub.
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_file(tmp_audio_path)
        wav_tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav_tmp_file.close()
        wav_tmp_path = wav_tmp_file.name
        sound.export(wav_tmp_path, format="wav")
    except Exception as conv_e:
        print("Audio conversion failed:", conv_e)
        wav_tmp_path = tmp_audio_path
    
    # Transcribe the audio using SpeechRecognition.
    try:
        with sr.AudioFile(wav_tmp_path) as source:
            audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data)
        print("Transcription:", transcription)
    except Exception as trans_e:
        try:
            os.remove(tmp_audio_path)
        except Exception as e:
            print("Error deleting original temp audio file:", e)
        try:
            if wav_tmp_path != tmp_audio_path:
                os.remove(wav_tmp_path)
        except Exception as e:
            print("Error deleting WAV temp file:", e)
        DeniedLog.objects.create(user=user, room=room, reason=f"Voice transcription failed: {trans_e}")
        return Response({'error': f"Voice transcription failed: {trans_e}"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Compute transcription similarity.
    similarity = difflib.SequenceMatcher(None, transcription.lower(), expected_sentence.lower()).ratio()
    similarity_pct = round(similarity * 100)
    print("Transcription similarity:", similarity_pct, "%")
    
    if not user.voice_reference:
        DeniedLog.objects.create(user=user, room=room, reason="No voice reference available.")
        return Response({'error': 'No voice reference available. Please enroll your voice.'}, status=status.HTTP_400_BAD_REQUEST)
    
    verified, speaker_similarity = verify_speaker(wav_tmp_path, user.voice_reference.path)
    speaker_similarity_pct = round(speaker_similarity * 100)
    
    deepfake_verified = detect_deepfake(wav_tmp_path)
    
    voice_verified = (similarity >= 0.80) and verified and deepfake_verified
    
    try:
        os.remove(tmp_audio_path)
    except Exception as e:
        print("Error deleting original temp audio file:", e)
    try:
        if wav_tmp_path != tmp_audio_path:
            os.remove(wav_tmp_path)
    except Exception as e:
        print("Error deleting WAV temp file:", e)
    
    if voice_verified:
        AccessLog.objects.create(
            user=user,
            room=room,
            remarks=f"Transcription similarity: {similarity_pct}%, Speaker similarity: {speaker_similarity_pct}%, Deepfake: {'Not Deepfake' if deepfake_verified else 'Deepfake'}"
        )
        return Response({'message': 'Access Granted'})
    else:
        DeniedLog.objects.create(
            user=user,
            room=room,
            reason=f"Voice verification failed. Transcription similarity: {similarity_pct}%, Speaker similarity: {speaker_similarity_pct}%"
        )
        return Response({'message': 'Access Denied'}, status=status.HTTP_401_UNAUTHORIZED)

# ------------------ Administrative Endpoints ------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_access_logs(request):
    if not request.user.is_admin:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    granted_logs = AccessLog.objects.all().order_by('-timestamp')
    denied_logs = DeniedLog.objects.all().order_by('-timestamp')
    granted_serializer = AccessLogSerializer(granted_logs, many=True)
    denied_serializer = DeniedLogSerializer(denied_logs, many=True)
    return Response({
        'access_logs': granted_serializer.data,
        'denied_logs': denied_serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    if not request.user.is_admin:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    name = request.data.get('name')
    room_id = request.data.get('room_id', '')
    group_id = request.data.get('group_id')
    if not name or not group_id:
        return Response({'error': 'Room name and group id are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        group = RoomGroup.objects.get(id=group_id)
    except RoomGroup.DoesNotExist:
        return Response({'error': 'Room group not found'}, status=status.HTTP_404_NOT_FOUND)
    room = Room(name=name, room_id=room_id, group=group)
    room.save()
    serializer = RoomSerializer(room)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
