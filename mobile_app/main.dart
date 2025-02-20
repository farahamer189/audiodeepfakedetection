import 'package:flutter/material.dart';
import 'get_started.dart'; // Ensure this is correctly imported

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Your App Name',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: GetStartedPage(), // THIS SHOULD BE THE FIRST PAGE
    );
  }
}
