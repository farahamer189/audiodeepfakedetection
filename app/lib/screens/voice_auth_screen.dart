import 'dart:typed_data';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io' show File;
import 'dart:async';
import 'dart:html' as html;

class VoiceAuthScreen extends StatefulWidget {
  final String roomId;
  final String challengeSentence;
  const VoiceAuthScreen({Key? key, required this.roomId, required this.challengeSentence}) : super(key: key);
  
  @override
  _VoiceAuthScreenState createState() => _VoiceAuthScreenState();
}

class _VoiceAuthScreenState extends State<VoiceAuthScreen> {
  final Record _record = Record();
  bool _isRecording = false;
  Uint8List? _recordedBytes;
  bool _loading = false;
  String? _errorMessage;
  String? _authResult;
  
  @override
  void dispose() {
    _record.dispose();
    super.dispose();
  }
  
  Future<void> _startRecording() async {
    bool hasPermission = await _record.hasPermission();
    if (!hasPermission) {
      setState(() {
        _errorMessage = "Microphone permission not granted.";
      });
      return;
    }
    await _record.start();
    setState(() {
      _isRecording = true;
    });
  }
  
  Future<void> _stopRecording() async {
    String? path = await _record.stop();
    setState(() {
      _isRecording = false;
    });
    if (path != null) {
      if (!kIsWeb) {
        File file = File(path);
        _recordedBytes = await file.readAsBytes();
      } else {
        try {
          final request = await html.HttpRequest.request(
            path,
            responseType: "arraybuffer",
          );
          if (request.response is ByteBuffer) {
            final byteBuffer = request.response as ByteBuffer;
            setState(() {
              _recordedBytes = Uint8List.view(byteBuffer);
            });
          } else {
            setState(() {
              _recordedBytes = request.response;
            });
          }
        } catch (e) {
          setState(() {
            _errorMessage = "Error retrieving recorded audio: $e";
          });
        }
      }
    }
  }
  
  Future<void> _submitVoiceAuth() async {
    if (_recordedBytes == null) {
      setState(() {
        _errorMessage = "No audio recorded.";
      });
      return;
    }
    setState(() {
      _loading = true;
      _errorMessage = null;
      _authResult = null;
    });
    try {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('access_token') ?? '';
      final uri = Uri.parse('http://localhost:8000/api/biometric-auth/voice/');
      final request = http.MultipartRequest('POST', uri);
      request.headers['Authorization'] = 'Bearer $token';
      request.fields['room_id'] = widget.roomId;
      request.fields['expected_sentence'] = widget.challengeSentence;
      request.files.add(http.MultipartFile.fromBytes('audio_sample', _recordedBytes!, filename: "voice.wav"));
      
      final response = await request.send();
      final respBody = await http.Response.fromStream(response);
      if (response.statusCode == 200) {
        setState(() {
          _authResult = "Access Granted";
        });
      } else {
        setState(() {
          _authResult = "Access Denied";
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Error during voice authentication: $e";
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Voice Authentication"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text("Challenge Sentence:", style: TextStyle(fontSize: 18)),
            const SizedBox(height: 8),
            Text(
              widget.challengeSentence,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            if (_isRecording)
              const Text("Recording...", style: TextStyle(color: Colors.red, fontSize: 18)),
            if (!_isRecording)
              ElevatedButton(
                onPressed: _startRecording,
                child: const Text("Start Recording"),
              ),
            const SizedBox(height: 10),
            if (_isRecording)
              ElevatedButton(
                onPressed: _stopRecording,
                child: const Text("Stop Recording"),
              ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _submitVoiceAuth,
              child: _loading ? const CircularProgressIndicator() : const Text("Submit Voice Authentication"),
            ),
            const SizedBox(height: 20),
            if (_errorMessage != null)
              Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
            if (_authResult != null)
              Text("Authentication Result: $_authResult", style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
