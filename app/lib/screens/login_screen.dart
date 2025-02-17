import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'face_auth_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);
  
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;
  String? _errorMessage;
  
  Future<void> _login() async {
    setState(() {
      _loading = true;
      _errorMessage = null;
    });
    final username = _usernameController.text.trim();
    final password = _passwordController.text.trim();
    
    if (username.isEmpty || password.isEmpty) {
      setState(() {
        _errorMessage = "Username and password cannot be empty.";
        _loading = false;
      });
      return;
    }
    
    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['access'];
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', token);
        // Also store the username for later use.
        await prefs.setString('username', username);
        // For this example, we automatically navigate to the Face Auth screen for room "caac3763"
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => const FaceAuthScreen(roomId: "caac3763"),
          ),
        );
      } else {
        setState(() {
          _errorMessage = "Login failed: ${response.body}";
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Error during login: $e";
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
      appBar: AppBar(title: const Text("Login")),
      body: Padding(
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
            if (_errorMessage != null)
              Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loading ? null : _login,
              child: _loading ? const CircularProgressIndicator() : const Text("Login"),
            ),
          ],
        ),
      ),
    );
  }
}
