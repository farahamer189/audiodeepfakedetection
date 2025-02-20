import 'package:flutter/material.dart';

class FaceScanPage extends StatelessWidget {
  final String username;

  FaceScanPage({required this.username});

  @override
  Widget build(BuildContext context) {
    // Simulate the face scan process
    bool isRecognized = true; // Simulate successful face recognition
    bool hasAccess = true; // Simulate access rights

    return Scaffold(
      appBar: AppBar(
        title: Text('Face Scan'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Simulating face scan
            if (isRecognized)
              hasAccess
                  ? Column(
                      children: [
                        Text('Welcome, $username!'),
                        SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: () {
                            // Add liveness check functionality here
                          },
                          child: Text('Verify Liveness'),
                        ),
                      ],
                    )
                  : Text(
                      'Access Denied, Dear $username, you don’t have access to this room.',
                      style: TextStyle(color: Colors.red),
                    )
            else
              Text(
                'Access Denied, user cannot be recognized.',
                style: TextStyle(color: Colors.red),
              ),
          ],
        ),
      ),
    );
  }
}
