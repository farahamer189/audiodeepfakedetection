import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(BioAccessApp());
}

class BioAccessApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BioAccess',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const LoginScreen(),
    );
  }
}
