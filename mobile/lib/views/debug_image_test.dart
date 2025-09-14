import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../widgets/adaptive_image.dart';

class DebugImageTest extends StatelessWidget {
  const DebugImageTest({super.key});

  @override
  Widget build(BuildContext context) {
    debugPrint('🔍 DebugImageTest: Construction du widget de test');

    // Une image base64 de test très simple (pixel blanc 1x1)
    const testImageBase64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Test Image Debug'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Test d\'affichage d\'images',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            const Text('1. Image base64 simple (pixel blanc):'),
            const SizedBox(height: 10),
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.red, width: 2),
              ),
              child: const AdaptiveImage(
                imageBase64: testImageBase64,
                width: 100,
                height: 100,
              ),
            ),
            const SizedBox(height: 20),
            const Text('2. Image d\'erreur (AdaptiveImage sans données):'),
            const SizedBox(height: 10),
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.blue, width: 2),
              ),
              child: const AdaptiveImage(
                width: 100,
                height: 100,
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                debugPrint('🔍 Bouton de test cliqué');
              },
              child: const Text('Test Log'),
            ),
          ],
        ),
      ),
    );
  }
}