import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class UserService {
  static const String _currentUserKey = 'current_user';
  static const String _currentUserIdKey = 'current_user_id';
  
  final ApiService _apiService;
  
  UserService(this._apiService);
  
  // Cache de l'utilisateur actuel
  Map<String, dynamic>? _currentUser;
  int? _currentUserId;
  
  /// Récupère l'utilisateur actuel depuis l'API et le met en cache
  Future<Map<String, dynamic>?> getCurrentUser({bool forceRefresh = false}) async {
    if (_currentUser != null && !forceRefresh) {
      return _currentUser;
    }
    
    try {
      final user = await _apiService.getCurrentUser();
      _currentUser = user;
      _currentUserId = user['id'] as int?;
      
      // Sauvegarder en cache local
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_currentUserKey, jsonEncode(user));
      if (_currentUserId != null) {
        await prefs.setInt(_currentUserIdKey, _currentUserId!);
      }
      
      return _currentUser;
    } catch (e) {
      // En cas d'erreur, essayer de récupérer depuis le cache local
      final prefs = await SharedPreferences.getInstance();
      final cachedUser = prefs.getString(_currentUserKey);
      if (cachedUser != null) {
        _currentUser = jsonDecode(cachedUser);
        _currentUserId = prefs.getInt(_currentUserIdKey);
        return _currentUser;
      }
      rethrow;
    }
  }
  
  /// Récupère l'ID de l'utilisateur actuel
  Future<int?> getCurrentUserId({bool forceRefresh = false}) async {
    if (_currentUserId != null && !forceRefresh) {
      return _currentUserId;
    }
    
    final user = await getCurrentUser(forceRefresh: forceRefresh);
    return user?['id'] as int?;
  }
  
  /// Vérifie si l'utilisateur est connecté
  Future<bool> isLoggedIn() async {
    try {
      final user = await getCurrentUser();
      return user != null;
    } catch (e) {
      return false;
    }
  }
  
  /// Supprime l'utilisateur du cache (déconnexion)
  Future<void> clearUser() async {
    _currentUser = null;
    _currentUserId = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_currentUserKey);
    await prefs.remove(_currentUserIdKey);
  }
  
  /// Vérifie si un message appartient à l'utilisateur actuel
  Future<bool> isMessageFromCurrentUser(int? senderId) async {
    if (senderId == null) return false;
    final currentUserId = await getCurrentUserId();
    return currentUserId != null && senderId == currentUserId;
  }
} 