import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  static const String _prodApiUrl = 'https://arosaje-backend-t2x7.onrender.com';
  static const String _devApiUrl = 'http://localhost:8000';
  
  /// Récupère l'URL de l'API selon l'environnement
  static String get apiUrl {
    if (kIsWeb) {
      // Pour le web (Netlify), utiliser toujours l'API de production
      return _prodApiUrl;
    } else {
      // Pour mobile, utiliser dotenv si disponible, sinon production
      return dotenv.env['FLUTTER_API_URL'] ?? _prodApiUrl;
    }
  }
  
  /// Nom de l'application
  static String get appName {
    if (kIsWeb) {
      return 'Arosa-je Web';
    } else {
      return dotenv.env['FLUTTER_APP_NAME'] ?? 'Arosa-je Mobile';
    }
  }
  
  /// Mode debug
  static bool get isDebug {
    if (kIsWeb) {
      return false; // Désactiver le debug en production web
    } else {
      return dotenv.env['FLUTTER_DEBUG']?.toLowerCase() == 'true';
    }
  }
}