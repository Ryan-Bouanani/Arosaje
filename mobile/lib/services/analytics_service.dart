import 'dart:convert';
import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/services/api_service.dart';

/// Service d'analytics conforme RGPD pour l'application mobile
/// 
/// Toutes les données collectées sont anonymisées et ne permettent pas
/// l'identification des utilisateurs individuels.
class AnalyticsService {
  final ApiService _apiService;
  static const String _sessionKey = 'analytics_session';
  static const String _userHashKey = 'user_hash';
  static const String _saltKey = 'arosaje_mobile_salt_2024';
  
  String? _sessionHash;
  String? _userHash;
  String? _deviceType;
  String? _appVersion;

  AnalyticsService(this._apiService);

  /// Initialise le service d'analytics
  Future<void> initialize() async {
    await _initializeSession();
    await _initializeDeviceInfo();
    await _initializeAppInfo();
  }

  /// Initialise une session anonymisée
  Future<void> _initializeSession() async {
    final prefs = await SharedPreferences.getInstance();
    
    // Génère un hash de session unique et anonyme
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final sessionId = '$timestamp-${Platform.isIOS ? "ios" : "android"}';
    _sessionHash = _generateHash(sessionId);
    
    await prefs.setString(_sessionKey, _sessionHash!);
  }

  /// Initialise les informations anonymisées de l'utilisateur
  Future<void> initializeUser(String? userId) async {
    if (userId != null) {
      _userHash = _generateHash(userId);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userHashKey, _userHash!);
    }
  }

  /// Initialise les informations de l'appareil (anonymisées)
  Future<void> _initializeDeviceInfo() async {
    final deviceInfo = DeviceInfoPlugin();
    
    if (Platform.isIOS) {
      final iosInfo = await deviceInfo.iosInfo;
      _deviceType = 'iOS-${iosInfo.systemVersion}';
    } else if (Platform.isAndroid) {
      final androidInfo = await deviceInfo.androidInfo;
      _deviceType = 'Android-${androidInfo.version.release}';
    } else {
      _deviceType = 'Unknown';
    }
  }

  /// Initialise les informations de l'application
  Future<void> _initializeAppInfo() async {
    final packageInfo = await PackageInfo.fromPlatform();
    _appVersion = packageInfo.version;
  }

  /// Génère un hash SHA-256 anonymisé
  String _generateHash(String input) {
    final bytes = utf8.encode(input + _saltKey);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  /// Log un événement d'usage anonymisé
  Future<void> logEvent(String eventType, {
    Map<String, dynamic>? properties,
    String? feature,
    int? duration,
  }) async {
    try {
      final eventData = {
        'timestamp': DateTime.now().toIso8601String(),
        'event_type': eventType,
        'user_hash': _userHash,
        'session_hash': _sessionHash,
        'platform': 'mobile',
        'device_type': _deviceType,
        'app_version': _appVersion,
        'feature_used': feature,
        'duration_seconds': duration,
        'properties': _anonymizeProperties(properties ?? {}),
      };

      // Envoi vers l'API (endpoint de monitoring)
      await _apiService.post('/monitoring/events', data: eventData);
      
      print('Analytics event logged: $eventType'); // Debug message in English
    } catch (e) {
      print('Failed to log analytics event: $e'); // Debug message in English
    }
  }

  /// Anonymise les propriétés personnelles
  Map<String, dynamic> _anonymizeProperties(Map<String, dynamic> properties) {
    final anonymized = <String, dynamic>{};
    
    for (final entry in properties.entries) {
      final key = entry.key;
      final value = entry.value;
      
      // Anonymise les valeurs sensibles
      if (_isSensitiveKey(key)) {
        if (value is String && value.isNotEmpty) {
          anonymized[key] = _generateHash(value);
        }
      } else {
        anonymized[key] = value;
      }
    }
    
    return anonymized;
  }

  /// Vérifie si une clé contient des données sensibles
  bool _isSensitiveKey(String key) {
    final sensitiveKeys = [
      'user_id', 'email', 'name', 'phone', 'address',
      'location', 'coordinates', 'ip', 'personal'
    ];
    
    return sensitiveKeys.any((sensitive) => 
        key.toLowerCase().contains(sensitive));
  }

  /// Log le démarrage d'une session
  Future<void> logSessionStart() async {
    await logEvent('session_start', properties: {
      'startup_time': DateTime.now().millisecondsSinceEpoch,
    });
  }

  /// Log la fin d'une session avec la durée
  Future<void> logSessionEnd(Duration sessionDuration) async {
    await logEvent('session_end', 
      duration: sessionDuration.inSeconds,
      properties: {
        'session_duration_ms': sessionDuration.inMilliseconds,
      }
    );
  }

  /// Log l'utilisation d'une fonctionnalité
  Future<void> logFeatureUsage(String featureName, {
    Map<String, dynamic>? context,
  }) async {
    await logEvent('feature_usage', 
      feature: featureName,
      properties: context
    );
  }

  /// Log les erreurs et crashes (anonymisés)
  Future<void> logError(String errorType, String errorMessage, {
    String? stackTrace,
    String? pagePath,
  }) async {
    await logEvent('error', properties: {
      'error_type': errorType,
      'error_message': errorMessage,
      'stack_trace': stackTrace,
      'page_path': pagePath,
      'device_info': _deviceType,
    });
  }

  /// Log la navigation entre pages
  Future<void> logPageView(String pageName, {
    Map<String, dynamic>? pageProperties,
  }) async {
    await logEvent('page_view', properties: {
      'page_name': pageName,
      'timestamp': DateTime.now().toIso8601String(),
      ...?pageProperties,
    });
  }

  /// Log les métriques de performance
  Future<void> logPerformanceMetric(String metricType, int valueMs, {
    String? context,
  }) async {
    try {
      final performanceData = {
        'timestamp': DateTime.now().toIso8601String(),
        'metric_type': metricType,
        'value_ms': valueMs,
        'user_hash': _userHash,
        'session_hash': _sessionHash,
        'platform': 'mobile',
        'device_type': _deviceType,
        'context': context,
      };

      await _apiService.post('/monitoring/performance', data: performanceData);
    } catch (e) {
      print('Failed to log performance metric: $e'); // Debug message in English
    }
  }

  /// Nettoyage à la fermeture de l'application
  Future<void> dispose() async {
    // Log la fin de session si nécessaire
    // Ne pas conserver de données locales sensibles
  }
}

/// Extensions pour faciliter l'utilisation
extension AnalyticsPageRoute on AnalyticsService {
  /// Log automatique lors du changement de route
  Future<void> logRouteChange(String routeName, String? previousRoute) async {
    await logPageView(routeName, pageProperties: {
      'previous_route': previousRoute,
      'navigation_time': DateTime.now().toIso8601String(),
    });
  }
}

/// Constantes pour les types d'événements
class AnalyticsEvents {
  static const String login = 'login';
  static const String logout = 'logout';
  static const String plantCreate = 'plant_create';
  static const String plantView = 'plant_view';
  static const String messagesSend = 'message_send';
  static const String photoUpload = 'photo_upload';
  static const String settingsChange = 'settings_change';
  static const String searchPerformed = 'search_performed';
  static const String errorOccurred = 'error_occurred';
}

/// Constantes pour les noms de fonctionnalités
class AnalyticsFeatures {
  static const String plantManagement = 'plant_management';
  static const String messaging = 'messaging';
  static const String photoCapture = 'photo_capture';
  static const String userProfile = 'user_profile';
  static const String settings = 'settings';
  static const String search = 'search';
  static const String notifications = 'notifications';
} 