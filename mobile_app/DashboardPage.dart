import 'package:flutter/material.dart';
import 'Login_Page.dart'; // Import the Login Page

class DashboardPage extends StatelessWidget {
  final String username;
  final String role;

  // Constructor to accept passed details
  const DashboardPage({Key? key, required this.username, required this.role}) : super(key: key);

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
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center, // Center the content vertically
            crossAxisAlignment: CrossAxisAlignment.center, // Center the content horizontally
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
                      MaterialPageRoute(builder: (context) => LoginPage()),
                    );
                  },
                ),
              ),
              Text(
                'Welcome, $username!',
                style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold, color: Colors.white, fontFamily: 'DancingScript'), // Text color white
              ),
              SizedBox(height: 10),
              Text(
                'Dashboard', // Display "Dashboard" under "Welcome"
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white, fontFamily: 'DancingScript'), // Bold "Dashboard"
              ),
              SizedBox(height: 30),
              // Show different buttons based on the role
              ...[
                if (role == 'admin') ...[
                  ElevatedButton(
                    onPressed: () {
                      // Add logic for Manage Users button
                    },
                    child: Text(
                      'Manage Users',
                      style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white), // White text
                    ),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
                      backgroundColor: const Color.fromARGB(255, 1, 16, 42),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
                    ),
                  ),
                  SizedBox(height: 20), // Increase spacing between buttons
                  ElevatedButton(
                    onPressed: () {
                      // Add logic for Manage Room Numbers button
                    },
                    child: Text(
                      'Manage Room Numbers',
                      style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white), // White text
                    ),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
                      backgroundColor: const Color.fromARGB(255, 1, 16, 42),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
                    ),
                  ),
                  SizedBox(height: 20), // Increase spacing between buttons
                  ElevatedButton(
                    onPressed: () {
                      // Add logic for Access Record button
                    },
                    child: Text(
                      'Access Record',
                      style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white), // White text
                    ),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
                      backgroundColor: const Color.fromARGB(255, 1, 16, 42),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
                    ),
                  ),
                ],
                if (role == 'user') ...[
                  ElevatedButton(
                    onPressed: () {
                      // Add logic for QR code scanning button
                    },
                    child: Text(
                      'Scan QR Code',
                      style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white), // White text
                    ),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
                      backgroundColor: const Color.fromARGB(255, 1, 16, 42),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(25)),
                    ),
                  ),
                ],
              ],
              SizedBox(height: 20), // Add some spacing below buttons
            ],
          ),
        ),
      ),
    );
  }
}
