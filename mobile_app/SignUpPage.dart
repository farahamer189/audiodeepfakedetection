import 'package:flutter/material.dart';
import 'get_started.dart'; // Import the Get Started Page

class SignUpPage extends StatefulWidget {
  @override
  _SignUpPageState createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _emailController = TextEditingController();

  bool _isPasswordVisible = false;
  bool _isConfirmPasswordVisible = false;

  String _selectedGender = 'Male'; 


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [const Color.fromARGB(255, 9, 5, 88), const Color.fromARGB(255, 109, 88, 153)], // Same background as Login Page
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Stack(
          children: [
            // Back Button (Top Left)
            Positioned(
              top: 40, // Adjust position as needed
              left: 16,
              child: IconButton(
                icon: Icon(Icons.arrow_back, color: Colors.white, size: 30),
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => GetStartedPage()), // ✅ Navigate to Get Started Page
                  );
                },
              ),
            ),

            // Sign Up Form
            Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: SingleChildScrollView(
                  child: Form(
                    key: _formKey,
                    child: Column(
                      children: [
                        Text(
                          'Sign Up',
                          style: TextStyle(
                            fontSize: 50,
                            fontWeight: FontWeight.bold,
                            color: Colors.white, 
                            fontFamily: 'DancingScript',
                          ),
                          textAlign: TextAlign.center,
                        ),
                        SizedBox(height: 20),

                        // Username Field
                        TextFormField(
                          controller: _usernameController,
                          style: TextStyle(color: Colors.white), // Text color white
                          decoration: InputDecoration(
                            labelText: 'Username',
                            labelStyle: TextStyle(color: Colors.white), // Label color white
                            enabledBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.white), // White border
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.blueAccent),
                            ),
                          ),
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Please enter your username';
                            }
                            return null;
                          },
                        ),
                        SizedBox(height: 20),

                        // Email Field
                        TextFormField(
                          controller: _emailController,
                          style: TextStyle(color: Colors.white), // Text color white
                          decoration: InputDecoration(
                            labelText: 'Email',
                            labelStyle: TextStyle(color: Colors.white), // Label color white
                            enabledBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.white), // White border
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.blueAccent),
                            ),
                          ),
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Please enter your email';
                            }
                            if (!RegExp(r'\S+@\S+\.\S+').hasMatch(value)) {
                              return 'Please enter a valid email address';
                            }
                            return null;
                          },
                        ),
                        SizedBox(height: 20),

                        // Password Field
                        TextFormField(
                          controller: _passwordController,
                          obscureText: !_isPasswordVisible,
                          style: TextStyle(color: Colors.white), // Text color white
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

                        // Confirm Password Field
                        TextFormField(
                          controller: _confirmPasswordController,
                          obscureText: !_isConfirmPasswordVisible,
                          style: TextStyle(color: Colors.white), // Text color white
                          decoration: InputDecoration(
                            labelText: 'Confirm Password',
                            labelStyle: TextStyle(color: Colors.white),
                            suffixIcon: IconButton(
                              icon: Icon(
                                _isConfirmPasswordVisible ? Icons.visibility : Icons.visibility_off,
                                color: Colors.white,
                              ),
                              onPressed: () {
                                setState(() {
                                  _isConfirmPasswordVisible = !_isConfirmPasswordVisible;
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
                              return 'Please confirm your password';
                            }
                            if (value != _passwordController.text) {
                              return 'Passwords do not match';
                            }
                            return null;
                          },
                        ),
                        SizedBox(height: 20),

                        // Gender Dropdown
                        DropdownButtonFormField<String>(
                          value: _selectedGender,
                          dropdownColor: Colors.black, // Dropdown background
                          icon: Icon(Icons.arrow_drop_down, color: Colors.white), // Dropdown icon color
                          style: TextStyle(color: Colors.white), // Dropdown text color
                          items: ['Male', 'Female']
                              .map((gender) => DropdownMenuItem<String>(
                                    value: gender,
                                    child: Text(gender, style: TextStyle(color: Colors.white)), // White text
                                  ))
                              .toList(),
                          onChanged: (value) {
                            setState(() {
                              _selectedGender = value!;
                            });
                          },
                          decoration: InputDecoration(
                            labelText: 'Gender',
                            labelStyle: TextStyle(color: Colors.white), // Label color white
                            enabledBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.white),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderSide: BorderSide(color: Colors.blueAccent),
                            ),
                          ),
                        ),
                        SizedBox(height: 20),

                        // Sign Up Button
                        ElevatedButton(
  onPressed: () {
    if (_formKey.currentState!.validate()) {
      String username = _usernameController.text;
      String email = _emailController.text;
      String gender = _selectedGender;
      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            content: Text(
              'Sign Up Successful\nUsername: $username\nEmail: $email\nGender: $gender',
            ),
          );
        },
      );
    }
  },
  style: ElevatedButton.styleFrom(
    backgroundColor: const Color.fromARGB(255, 1, 16, 42),
    padding: EdgeInsets.symmetric(vertical: 20),  // Increased padding for a larger button
    minimumSize: Size(double.infinity, 60), // Adjusted the minimum size
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(25),
    ),
  ),
  child: Text(
    'Sign Up',
    style: TextStyle(fontSize: 18, color: Colors.white),
  ),
),
  
                      ],
                    ),
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
