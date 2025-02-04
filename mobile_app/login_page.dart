import 'package:flutter/material.dart';
import 'DashboardPage.dart'; // Import the DashboardPage
import 'get_started.dart'; // Import the GetStartedPage

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
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [const Color.fromARGB(255, 9, 5, 88), const Color.fromARGB(255, 109, 88, 153)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Stack(
          children: [
            // Back Button (Top Left)
           Positioned(
  top: 40,
  left: 16,
  child: IconButton(
    icon: Icon(Icons.arrow_back, color: Colors.white, size: 30),
    onPressed: () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => GetStartedPage()),
      );
    },
  ),
),


            // Login Form
            Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Login',
                        style: TextStyle(
                          fontSize: 50,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontFamily: 'DancingScript',
                        ),
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 20),
                      Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Dropdown menu
                            DropdownButtonFormField<String>(
                              value: _selectedRole,
                              dropdownColor: Colors.black,
                              icon: Icon(Icons.arrow_drop_down, color: Colors.white),
                              style: TextStyle(color: Colors.white),
                              items: ['user', 'admin']
                                  .map((role) => DropdownMenuItem<String>(
                                        value: role,
                                        child: Text(role.capitalize(), style: TextStyle(color: Colors.white)),
                                      ))
                                  .toList(),
                              onChanged: (value) {
                                setState(() {
                                  _selectedRole = value!;
                                });
                              },
                              decoration: InputDecoration(
                                labelText: 'Select Role',
                                labelStyle: TextStyle(color: Colors.white),
                                enabledBorder: OutlineInputBorder(
                                  borderSide: BorderSide(color: Colors.white),
                                ),
                                focusedBorder: OutlineInputBorder(
                                  borderSide: BorderSide(color: Colors.blueAccent),
                                ),
                              ),
                            ),
                            SizedBox(height: 20),

                            // Username field
                            TextFormField(
                              controller: _usernameController,
                              style: TextStyle(color: Colors.white),
                              decoration: InputDecoration(
                                labelText: 'Username',
                                labelStyle: TextStyle(color: Colors.white),
                                enabledBorder: OutlineInputBorder(
                                  borderSide: BorderSide(color: Colors.white),
                                ),
                                focusedBorder: OutlineInputBorder(
                                  borderSide: BorderSide(color: const Color.fromARGB(255, 207, 162, 246)),
                                ),
                              ),
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

                            // Password field
                            TextFormField(
                              controller: _passwordController,
                              style: TextStyle(color: Colors.white),
                              obscureText: !_isPasswordVisible,
                              decoration: InputDecoration(
                                labelText: 'Password',
                                labelStyle: TextStyle(color: Colors.white),
                                suffixIcon: IconButton(
                                  icon: Icon(
                                    _isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                                    color: Colors.white,
                                  ),
                                  onPressed: () {
                                    setState(() {
                                      _isPasswordVisible = !_isPasswordVisible;
                                    });
                                  },
                                ),
                                enabledBorder: OutlineInputBorder(
                                  borderSide: BorderSide(color: Colors.white),
                                ),
                                focusedBorder: OutlineInputBorder(
                                  borderSide: BorderSide(color: Colors.blueAccent),
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

                            // Login button
                            ElevatedButton(
                              onPressed: () {
                                if (_formKey.currentState!.validate()) {
                                  String username = _usernameController.text;
                                  String password = _passwordController.text;

                                  if ((_selectedRole == 'user' && password == userPassword) ||
                                      (_selectedRole == 'admin' && password == adminPassword)) {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (context) => DashboardPage(
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
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color.fromARGB(255, 1, 16, 42),
                                padding: EdgeInsets.symmetric(vertical: 15),
                              ),
                              child: Text(
                                'Login',
                                style: TextStyle(fontSize: 18, color: Colors.white),
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
          ],
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
