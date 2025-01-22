import 'package:flutter/material.dart';
import 'get_started.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      debugShowCheckedModeBanner: false,  // Disable the debug banner
      home: GetStartedPage(),  // The first screen that opens after the app starts
    );
  }
}
