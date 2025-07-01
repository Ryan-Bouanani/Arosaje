import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import 'storage_service.dart';
import 'api_service.dart';

class AuthService {
  static final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://localhost:8000';
  static AuthService? _instance;
  late final Dio _dio;
  late final StorageService _storageService;
  bool _isInitialized = false;

  // Constructeur privé
  AuthService._();

  // Factory pour le singleton
  static Future<AuthService> getInstance() async {
    if (_instance == null) {
      _instance = AuthService._();
      await _instance!._initializeService();
    }
    return _instance!;
  }

  Future<void> _initializeService() async {
    if (_isInitialized) return;

    final prefs = await SharedPreferences.getInstance();
    _storageService = StorageService(prefs);

    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 3),
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = _storageService.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ));

    _isInitialized = true;
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': email,
          'password': password,
        },
      );

      final data = json.decode(response.body);
      if (response.statusCode == 200) {
        await _storageService.saveToken(data['access_token']);
        return data;
      } else {
        throw Exception(data['detail'] ?? 'Échec de la connexion');
      }
    } catch (e) {
      throw Exception('Erreur de connexion: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String nom,
    required String prenom,
    required String telephone,
    required String role,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'nom': nom,
          'prenom': prenom,
          'telephone': telephone,
          'role': role,
        }),
      );

      final data = json.decode(response.body);
      if (response.statusCode == 200) {
        return data;
      } else {
        throw Exception(data['detail'] ?? 'Échec de l\'inscription');
      }
    } catch (e) {
      throw Exception('Erreur lors de l\'inscription: ${e.toString()}');
    }
  }

  Future<Map<String, dynamic>> getCurrentUser(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
      );

      final data = json.decode(response.body);
      if (response.statusCode == 200) {
        return data;
      } else {
        throw Exception(data['detail'] ?? 'Échec de la récupération du profil');
      }
    } catch (e) {
      throw Exception('Erreur lors de la récupération du profil: ${e.toString()}');
    }
  }

  Future<List<User>> getPendingAccounts() async {
    try {
      final token = _storageService.getToken();
      if (token == null) {
        throw Exception('Non authentifié');
      }

      final response = await _dio.get(
        '/admin/pending-verifications',
        options: Options(
          headers: {
            'Authorization': 'Bearer $token',
          },
        ),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => User.fromJson(json)).toList();
      }
      throw Exception('Erreur lors de la récupération des comptes en attente');
    } catch (e) {
      throw Exception('Erreur lors de la récupération des comptes en attente : $e');
    }
  }

  Future<void> verifyAccount(int userId) async {
    try {
      final token = _storageService.getToken();
      if (token == null) {
        throw Exception('Non authentifié');
      }

      final response = await _dio.post(
        '/admin/verify/$userId',
        options: Options(
          headers: {
            'Authorization': 'Bearer $token',
          },
        ),
      );

      if (response.statusCode != 200) {
        throw Exception('Erreur lors de la validation du compte');
      }
    } catch (e) {
      throw Exception('Erreur lors de la validation du compte : $e');
    }
  }

  Future<void> rejectAccount(int userId) async {
    try {
      final token = _storageService.getToken();
      if (token == null) {
        throw Exception('Non authentifié');
      }

      final response = await _dio.post(
        '/admin/reject/$userId',
        options: Options(
          headers: {
            'Authorization': 'Bearer $token',
          },
        ),
      );

      if (response.statusCode != 200) {
        throw Exception('Erreur lors du rejet du compte');
      }
    } catch (e) {
      throw Exception('Erreur lors du rejet du compte : $e');
    }
  }

  Future<void> logout() async {
    try {
      final apiService = ApiService();
      await apiService.logout();
      await _storageService.clearAll();
    } catch (e) {
      print('Erreur lors de la déconnexion : $e');
      // Même en cas d'erreur avec l'API, on nettoie les données locales
      await _storageService.clearAll();
      throw Exception('Erreur lors de la déconnexion : $e');
    }
  }
} 