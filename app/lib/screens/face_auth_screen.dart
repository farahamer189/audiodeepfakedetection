import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../widgets/webcam_widget.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'voice_auth_screen.dart';

class FaceAuthScreen extends StatefulWidget {
  final String roomId;
  const FaceAuthScreen({Key? key, required this.roomId}) : super(key: key);
  
  @override
  _FaceAuthScreenState createState() => _FaceAuthScreenState();
}

class _FaceAuthScreenState extends State<FaceAuthScreen> {
  Uint8List? capturedImage;
  bool _isSubmitting = false;
  String? _errorMessage;
  
  void onImageCaptured(Uint8List imageBytes) {
    setState(() {
      capturedImage = imageBytes;
    });
  }
  
  Future<void> _submitFaceAuth() async {
    if (capturedImage == null) {
      setState(() {
        _errorMessage = "No image captured.";
      });
      return;
    }
    
    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });
    
    try {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String token = prefs.getString('access_token') ?? '';
      String roomId = widget.roomId;
      
      var uri = Uri.parse('http://localhost:8000/api/biometric-auth/face/');
      var request = http.MultipartRequest('POST', uri);
      request.headers['Authorization'] = 'Bearer $token';
      request.fields['room_id'] = roomId;
      request.files.add(
          http.MultipartFile.fromBytes('face_image', capturedImage!,
              filename: 'face.png'));
      
      var response = await request.send();
      var respBody = await http.Response.fromStream(response);
      print("Face auth response: ${respBody.body}");
      
      if (response.statusCode == 200) {
        var data = jsonDecode(respBody.body);
        String challengeSentence = data['challenge_sentence'];
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) =>
                VoiceAuthScreen(roomId: roomId, challengeSentence: challengeSentence),
          ),
        );
      } else {
        setState(() {
          _errorMessage = "Face authentication failed: ${respBody.body}";
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Error during face authentication: $e";
      });
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Face Authentication")),
      body: Column(
        children: [
          Expanded(
            child: WebCamWidget(onImageCaptured: onImageCaptured),
          ),
          if (capturedImage != null)
            Container(
              height: 200,
              padding: const EdgeInsets.all(8.0),
              child: Image.memory(capturedImage!),
            ),
          if (_errorMessage != null)
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text(_errorMessage!,
                  style: const TextStyle(color: Colors.red)),
            ),
          const SizedBox(height: 10),
          ElevatedButton(
            onPressed: _isSubmitting ? null : _submitFaceAuth,
            child: _isSubmitting
                ? const CircularProgressIndicator()
                : const Text("Submit Face Authentication"),
          ),
          const SizedBox(height: 10),
        ],
      ),
    );
  }
}
