import 'package:flutter/material.dart';

class ForgotPasswordPage extends StatefulWidget {
  @override
  _ForgotPasswordPageState createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _emailController = TextEditingController();
  final _otpController = TextEditingController();
  bool _isOtpSent = false; // To check if OTP is sent
  bool _isOtpVerified = false; // To check if OTP is verified

  void _sendOtp() {
    // This is where you would send an OTP (e.g., via email or SMS)
    // Here we simulate sending an OTP
    setState(() {
      _isOtpSent = true;
    });
  }

  void _verifyOtp() {
    // Here you would verify the OTP entered by the user
    if (_otpController.text == '123456') {  // Simulated OTP check
      setState(() {
        _isOtpVerified = true;
      });
      // Proceed to reset the password
      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            content: Text('OTP Verified! You can now reset your password.'),
          );
        },
      );
    } else {
      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            content: Text('Invalid OTP. Please try again.'),
          );
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Forgot Password'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Enter your email to receive OTP for password reset',
                style: TextStyle(fontSize: 18),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 20),

              // Email Input Field
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'Email Address',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your email';
                  }
                  return null;
                },
              ),
              SizedBox(height: 20),

              // Send OTP Button
              ElevatedButton(
                onPressed: _sendOtp,
                child: Text('Send OTP'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                ),
              ),
              SizedBox(height: 20),

              // OTP Input Field
              if (_isOtpSent) ...[
                TextFormField(
                  controller: _otpController,
                  decoration: InputDecoration(
                    labelText: 'Enter OTP',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                ),
                SizedBox(height: 20),

                // Verify OTP Button
                ElevatedButton(
                  onPressed: _verifyOtp,
                  child: Text('Verify OTP'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                  ),
                ),
              ],

              // Reset Password Button (only shows after OTP is verified)
              if (_isOtpVerified) ...[
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () {
                    // Navigate to reset password page
                    // Or implement password reset logic here
                    showDialog(
                      context: context,
                      builder: (context) {
                        return AlertDialog(
                          content: Text('Please reset your password now.'),
                        );
                      },
                    );
                  },
                  child: Text('Reset Password'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
