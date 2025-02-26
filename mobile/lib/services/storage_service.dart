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
    return _prefs.getString(tokenKey);
  }

  String? getUserRole() {
    return _prefs.getString(userRoleKey);
  }

  Future<void> setToken(String token) async {
    await _prefs.setString('token', token);
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