import 'package:flutter/material.dart';

class ForgotPasswordPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Forgot Password'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Center(
        child: Text(
          'Forgot Password Page',
          style: TextStyle(fontSize: 24),
        ),
      ),
    );
  }
}
