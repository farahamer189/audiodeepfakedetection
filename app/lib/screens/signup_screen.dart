import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import 'login_screen.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({Key? key}) : super(key: key);
  @override
  _SignupScreenState createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _emailController = TextEditingController();
  bool _isAdmin = false;
  bool _loading = false;
  String? _errorMessage;

  XFile? _faceImage;
  XFile? _voiceReference;

  final ImagePicker _picker = ImagePicker();

  Future<void> _pickFaceImage() async {
    try {
      final image = await _picker.pickImage(source: ImageSource.camera);
      setState(() {
        _faceImage = image;
      });
    } catch (e) {
      setState(() {
        _errorMessage = "Failed to pick face image: $e";
      });
    }
  }

  Future<void> _pickVoiceReference() async {
    try {
      final file = await _picker.pickImage(source: ImageSource.gallery);
      setState(() {
        _voiceReference = file;
      });
    } catch (e) {
      setState(() {
        _errorMessage = "Failed to pick voice reference: $e";
      });
    }
  }

  Future<void> _signup() async {
    setState(() {
      _loading = true;
      _errorMessage = null;
    });
    if (_faceImage == null || _voiceReference == null) {
      setState(() {
        _errorMessage = "Please select both face image and voice reference.";
        _loading = false;
      });
      return;
    }
    try {
      await ApiService.signup(
        username: _usernameController.text.trim(),
        password: _passwordController.text.trim(),
        email: _emailController.text.trim(),
        isAdmin: _isAdmin,
        faceImagePath: _faceImage!.path,
        voiceReferencePath: _voiceReference!.path,
      );
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const LoginScreen()),
      );
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
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
      appBar: AppBar(title: const Text("Sign Up")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: "Username"),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: "Password"),
              obscureText: true,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: "Email"),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text("Register as Admin"),
              value: _isAdmin,
              onChanged: (value) {
                setState(() {
                  _isAdmin = value;
                });
              },
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _pickFaceImage,
              child: Text(_faceImage == null ? "Capture Face Image" : "Face Image Selected"),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _pickVoiceReference,
              child: Text(_voiceReference == null ? "Select Voice Reference" : "Voice Reference Selected"),
            ),
            const SizedBox(height: 16),
            if (_errorMessage != null)
              Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loading ? null : _signup,
              child: _loading ? const CircularProgressIndicator() : const Text("Sign Up"),
            ),
          ],
        ),
      ),
    );
  }
}
