import 'package:flutter/material.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';
import 'AuthenticationPage.dart'; // Authentication page

class ScanQRCodePage extends StatefulWidget {
  final String username;
  final String role;

  ScanQRCodePage({required this.username, required this.role});

  @override
  _ScanQRCodePageState createState() => _ScanQRCodePageState();
}

class _ScanQRCodePageState extends State<ScanQRCodePage> {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  QRViewController? controller;

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Scan QR Code on the Door'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Column(
        children: [
          Expanded(
            flex: 4,
            child: QRView(
              key: qrKey,
              onQRViewCreated: (QRViewController controller) {
                setState(() {
                  this.controller = controller;
                });
                controller.scannedDataStream.listen((scanData) {
                  // Access the QR code scan result
                  final qrCode = scanData.code;
                  if (qrCode != null) {
                    // Navigate to Authentication Page with scanned QR code, username, and role
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => AuthenticationPage(
                          username: widget.username,
                          qrData: qrCode,
                          role: widget.role,
                        ),
                      ),
                    );
                  } else {
                    // Handle error or invalid scan
                    print("Error scanning QR Code");
                  }
                });
              },
            ),
          ),
        ],
      ),
    );
  }
}
