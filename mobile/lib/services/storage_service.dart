import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String tokenKey = 'jwt_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userRoleKey = 'user_role';

  final SharedPreferences _prefs;

  StorageService._(this._prefs);

  static StorageService? _instance;
  
  static Future<StorageService> init() async {
    if (_instance == null) {
      final prefs = await SharedPreferences.getInstance();
      _instance = StorageService._(prefs);
    }
    return _instance!;
  }
  
  static Future<StorageService> getInstance() async {
    return _instance ?? await init();
  }

  Future<void> saveToken(String token) async {
    await _prefs.setString(tokenKey, token);
  }

  Future<void> saveUserRole(String role) async {
    await _prefs.setString(userRoleKey, role);
  }

  String? getToken() {
    // Essayer d'abord la clé principale, puis les alternatives
    return _prefs.getString(tokenKey) ?? 
           _prefs.getString('token') ?? 
           _prefs.getString('access_token');
  }

  String? getUserRole() {
    return _prefs.getString(userRoleKey);
  }

  Future<void> setToken(String token) async {
    // Utiliser la clé principale pour la cohérence
    await _prefs.setString(tokenKey, token);
  }

  Future<void> setUserId(int userId) async {
    await _prefs.setInt('userId', userId);
  }

  Future<int?> getUserId() async {
    return _prefs.getInt('userId');
  }

  Future<void> clearAll() async {
    await _prefs.clear();
  }

  Future<void> clear() async {
    await _prefs.clear();
  }

  // Méthodes pour le refresh token
  Future<void> saveRefreshToken(String refreshToken) async {
    await _prefs.setString(refreshTokenKey, refreshToken);
  }

  String? getRefreshToken() {
    return _prefs.getString(refreshTokenKey);
  }

  Future<void> clearRefreshToken() async {
    await _prefs.remove(refreshTokenKey);
  }

  // Méthode pour sauvegarder les deux tokens simultanément
  Future<void> saveTokens({
    required String accessToken, 
    required String refreshToken
  }) async {
    await Future.wait([
      saveToken(accessToken),
      saveRefreshToken(refreshToken),
    ]);
  }

  // Méthode pour vérifier si les tokens existent
  bool hasTokens() {
    return getToken() != null && getRefreshToken() != null;
  }

  // Méthode pour récupérer les deux tokens
  Map<String, String?> getTokens() {
    return {
      'access_token': getToken(),
      'refresh_token': getRefreshToken(),
    };
  }

  Future<void> clearTokens() async {
    await Future.wait([
      _prefs.remove(tokenKey),
      _prefs.remove(refreshTokenKey),
    ]);
  }
} 
