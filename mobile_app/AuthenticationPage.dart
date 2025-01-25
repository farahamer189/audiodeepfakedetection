import 'package:flutter/material.dart';

class AuthenticationPage extends StatelessWidget {
  final String username;
  final String qrData;
  final String role;

  // Constructor to receive parameters
  AuthenticationPage({
    required this.username,
    required this.qrData,
    required this.role,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Access for Room: $qrData'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text('Welcome $username!'),
            Text('Role: $role'),
            ElevatedButton(
              onPressed: () {
                // Handle verification logic here
              },
              child: Text('Verify Liveness'),
            ),
            // Optionally, add other buttons and features as per your requirements
          ],
        ),
      ),
    );
  }
}
