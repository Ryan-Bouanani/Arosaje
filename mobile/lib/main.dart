import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'widgets/adaptive_image.dart';

Future<void> main() async {
  print('🚀 MAIN: Application starting...');
  debugPrint('🚀 MAIN: Application starting (debugPrint)...');

  try {
    WidgetsFlutterBinding.ensureInitialized();
    print('✅ MAIN: WidgetsFlutterBinding initialized');

    runApp(const MyApp());
    print('✅ MAIN: runApp called');
  } catch (e, stack) {
    print('❌ MAIN ERROR: $e');
    print('❌ MAIN STACK: $stack');
    // Essayer de démarrer quand même avec une app minimale
    runApp(MaterialApp(
      home: Scaffold(
        body: Center(
          child: Text('Error: $e'),
        ),
      ),
    ));
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    print('🏗️ MYAPP: Building MyApp widget');
    debugPrint('🏗️ MYAPP: Building MyApp widget (debugPrint)');

    try {
      return MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'A\'rosa-je',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.green,
            brightness: Brightness.light,
          ),
          useMaterial3: true,
        ),
        home: const TestScreen(),
      );
    } catch (e, stack) {
      print('❌ MYAPP ERROR: $e');
      print('❌ MYAPP STACK: $stack');
      return MaterialApp(
        home: Scaffold(
          body: Center(
            child: Text('MyApp Error: $e'),
          ),
        ),
      );
    }
  }
}

class TestScreen extends StatelessWidget {
  const TestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    print('🔥 TESTSCREEN: Building TestScreen');
    debugPrint('🔥 TESTSCREEN: Building TestScreen (debugPrint)');

    // Image base64 de test simple et valide (carré rouge 2x2)
    const testImageBase64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIHWPYf+M/AzYwigRSRgEAOoACYXDJcPkAAAAASUVORK5CYII=';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Test Image Debug'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('🎯 Application Flutter Démarrée!'),
            const SizedBox(height: 20),
            const Text('✅ Test de logs réussi'),
            const SizedBox(height: 30),
            const Text('Test d\'affichage d\'images:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            const Text('1. Image base64 test (carré rouge 2x2):'),
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
            const Text('3. Test Image.network avec data URI:'),
            const SizedBox(height: 10),
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.purple, width: 2),
              ),
              child: Image.network(
                testImageBase64,
                fit: BoxFit.cover,
                width: 100,
                height: 100,
                errorBuilder: (context, error, stackTrace) {
                  print('❌ Image.network: Erreur: $error');
                  return Container(
                    color: Colors.purple[100],
                    child: const Icon(Icons.error),
                  );
                },
              ),
            ),
            const SizedBox(height: 20),
            const Text('4. Test avec vraie photo de plante (API):'),
            const SizedBox(height: 10),
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.green, width: 2),
              ),
              child: const AdaptiveImage(
                imageBase64: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCABkAGQDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+/iiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/2Q==',
                plantId: 7, // ID de plante de test avec image
                width: 100,
                height: 100,
                fit: BoxFit.cover,
              ),
            ),
            const SizedBox(height: 20),
            const Text('5. Test proxy direct (plante ID 7):'),
            const SizedBox(height: 10),
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.orange, width: 2),
              ),
              child: Image.network(
                'https://arosaje-backend-t2x7.onrender.com/plants/7/image',
                fit: BoxFit.cover,
                width: 100,
                height: 100,
                errorBuilder: (context, error, stackTrace) {
                  print('❌ Image proxy direct: Erreur: $error');
                  return Container(
                    color: Colors.orange[100],
                    child: const Icon(Icons.error),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
