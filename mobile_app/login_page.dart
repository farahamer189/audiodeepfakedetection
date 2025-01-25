import 'package:flutter/material.dart';
import 'ScanQRCodePage.dart'; // Import the ScanQRCodePage

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  String _selectedRole = 'user'; 
  bool _isPasswordVisible = false; 

  final String userUsername = "name@user";
  final String userPassword = "userPassword";
  final String adminUsername = "name@admin";
  final String adminPassword = "adminPassword";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Login'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Welcome to Our Access Control System',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'ChintaRetro', 
                  ),
                ),
                SizedBox(height: 30),
                Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      DropdownButtonFormField<String>(
                        value: _selectedRole,
                        items: ['user', 'admin']
                            .map((role) => DropdownMenuItem<String>(
                                  value: role,
                                  child: Text(role.capitalize()),
                                ))
                            .toList(),
                        onChanged: (value) {
                          setState(() {
                            _selectedRole = value!;
                          });
                        },
                        decoration: InputDecoration(labelText: 'Select Role'),
                      ),
                      SizedBox(height: 20),
                      TextFormField(
                        controller: _usernameController,
                        decoration: InputDecoration(labelText: 'Username'),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your username';
                          }
                          if ((_selectedRole == 'user' && value != userUsername) ||
                              (_selectedRole == 'admin' && value != adminUsername)) {
                            return 'Invalid username for the selected role';
                          }
                          return null;
                        },
                      ),
                      SizedBox(height: 20),
                      TextFormField(
                        controller: _passwordController,
                        obscureText: !_isPasswordVisible,
                        decoration: InputDecoration(
                          labelText: 'Password',
                          suffixIcon: IconButton(
                            icon: Icon(
                              _isPasswordVisible
                                  ? Icons.visibility
                                  : Icons.visibility_off,
                            ),
                            onPressed: () {
                              setState(() {
                                _isPasswordVisible = !_isPasswordVisible;
                              });
                            },
                          ),
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your password';
                          }
                          return null;
                        },
                      ),
                      SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: () {
                          if (_formKey.currentState!.validate()) {
                            String username = _usernameController.text;
                            String password = _passwordController.text;

                            // Validate the entered password based on the selected role
                            if ((_selectedRole == 'user' && password == userPassword) ||
                                (_selectedRole == 'admin' && password == adminPassword)) {
                              // Navigate to Scan QR Code page and pass username and role
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => ScanQRCodePage(
                                    username: username,
                                    role: _selectedRole,
                                  ),
                                ),
                              );
                            } else {
                              showDialog(
                                context: context,
                                builder: (context) {
                                  return AlertDialog(
                                    content: Text('Invalid password.'),
                                  );
                                },
                              );
                            }
                          }
                        },
                        child: Text('Login'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Color.fromARGB(255, 238, 239, 240),
                          padding: EdgeInsets.symmetric(vertical: 15),
                          textStyle: TextStyle(fontSize: 18),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

extension StringCasingExtension on String {
  String capitalize() {
    return this.isEmpty ? this : this[0].toUpperCase() + this.substring(1);
  }
}
