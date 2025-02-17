import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';

class WebCamWidget extends StatefulWidget {
  final Function(Uint8List imageBytes) onImageCaptured;
  const WebCamWidget({Key? key, required this.onImageCaptured}) : super(key: key);
  
  @override
  _WebCamWidgetState createState() => _WebCamWidgetState();
}

class _WebCamWidgetState extends State<WebCamWidget> {
  CameraController? _controller;
  Future<void>? _initializeControllerFuture;
  List<CameraDescription>? cameras;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      cameras = await availableCameras();
      if (cameras != null && cameras!.isNotEmpty) {
        // Use the front camera if available.
        CameraDescription frontCamera = cameras!.firstWhere(
          (camera) => camera.lensDirection == CameraLensDirection.front,
          orElse: () => cameras!.first,
        );
        _controller = CameraController(frontCamera, ResolutionPreset.medium);
        _initializeControllerFuture = _controller!.initialize();
        if (!mounted) return;
        setState(() {});
      }
    } catch (e) {
      print("Error initializing camera: $e");
    }
  }

  Future<void> _captureImage() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    try {
      await _initializeControllerFuture;
      XFile file = await _controller!.takePicture();
      Uint8List bytes = await file.readAsBytes();
      widget.onImageCaptured(bytes);
    } catch (e) {
      print("Error capturing image: $e");
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return _controller == null
        ? const Center(child: Text("Loading camera..."))
        : FutureBuilder<void>(
            future: _initializeControllerFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.done) {
                return Stack(
                  children: [
                    CameraPreview(_controller!),
                    Positioned(
                      bottom: 20,
                      left: 0,
                      right: 0,
                      child: Center(
                        child: ElevatedButton(
                          onPressed: _captureImage,
                          child: const Text("Capture Image"),
                        ),
                      ),
                    ),
                  ],
                );
              } else {
                return const Center(child: CircularProgressIndicator());
              }
            },
          );
  }
}
