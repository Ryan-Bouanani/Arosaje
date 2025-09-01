import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String tokenKey = 'jwt_token';
  static const String userRoleKey = 'user_role';

  final SharedPreferences _prefs;

  StorageService(this._prefs);

  static Future<StorageService> init() async {
    final prefs = await SharedPreferences.getInstance();
    return StorageService(prefs);
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
} 