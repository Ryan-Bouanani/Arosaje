import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  // 🔥 FORCE NETLIFY REBUILD - Unique content for asset detection
  static const String _buildSignature = 'FORCE_REBUILD_978b40d_v2_0_0_UNIQUE_HASH_15092025';
  static const int _buildTimestamp = 1726435800000; // Force unique compilation
  static const String _forceRebuildId = 'NETLIFY_BYPASS_STRATEGY_v10';
  
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
  
  /// Build signature for force rebuild detection
  static String get buildSignature => _buildSignature;
  
  /// Build timestamp for cache busting
  static int get buildTimestamp => _buildTimestamp;
  
  /// Force rebuild ID for Netlify bypass
  static String get forceRebuildId => _forceRebuildId;
  
  /// Get unique build info for debugging
  static Map<String, dynamic> get buildInfo => {
    'signature': _buildSignature,
    'timestamp': _buildTimestamp,
    'rebuildId': _forceRebuildId,
    'version': '2.0.0+15092025',
    'strategy': 'NETLIFY_BYPASS_v10'
  };
}