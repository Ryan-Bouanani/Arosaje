import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';
import 'dart:async';

class ApiService {
  // Pour WSL2, utilisez l'IP de l'hôte ou une IP accessible depuis l'émulateur
  static const String baseUrl = 'http://10.0.2.2:8000'; // Pour l'émulateur Android
  // Alternative: static const String baseUrl = 'http://192.168.1.100:8000'; // Remplacez par votre IP réseau

  String? _token;

  ApiService() {
    _initToken();
  }

  Future<void> _initToken() async {
    _token = await getToken();
  }

  Future<String?> getToken() async {
    if (_token != null) return _token;
    
    final prefs = await SharedPreferences.getInstance();
    // Essayer plusieurs clés possibles pour le token
    String? token = prefs.getString('jwt_token') ?? 
                   prefs.getString('token') ?? 
                   prefs.getString('access_token');
    
    if (token != null) {
      _token = token; // Mettre à jour le token en mémoire
    }
    
    print('Token retrieved: ${token != null ? "Found (length: ${token.length})" : "Not found"}');
    return token;
  }

  // Headers de base avec détection de plateforme
  Future<Map<String, String>> _getHeaders() async {
    final token = await getToken();
    final headers = {
      'Content-Type': 'application/json',
      'X-Platform': Platform.isIOS ? 'ios' : 'android',
      'X-Client-Platform': Platform.isIOS ? 'ios-app' : 'android-app',
      'User-Agent': 'Arosaje-Mobile-App/${Platform.isIOS ? "iOS" : "Android"}',
    };

    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }

    return headers;
  }

  // Méthode pour définir le token
  Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
  }

  // Méthode pour effacer le token
  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    await prefs.remove('token');
    await prefs.remove('access_token');
  }

  Future<dynamic> get(String endpoint, {Map<String, dynamic>? queryParameters}) async {
    try {
      final headers = await _getHeaders();
      
      Map<String, String> convertedParams = {};
      if (queryParameters != null) {
        convertedParams = queryParameters.map((key, value) => MapEntry(key, value.toString()));
      }
      
      final uri = Uri.parse('$baseUrl$endpoint').replace(queryParameters: convertedParams);
      
      print('Request headers: $headers');
      print('Request URL: $uri');
      
      final response = await http.get(
        uri,
        headers: headers,
      ).timeout(const Duration(seconds: 10));
      
      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 401) {
        await clearToken(); // Effacer le token en cas d'erreur d'authentification
        throw Exception('Authentication failed');
      } else {
        throw Exception('Failed to load data: ${response.statusCode}');
      }
    } catch (e) {
      print('Error in GET request: $e');
      rethrow;
    }
  }

  Future<dynamic> post(String endpoint, dynamic data) async {
    try {
      final headers = await _getHeaders();
      final uri = Uri.parse('$baseUrl$endpoint');
      
      final response = await http.post(
        uri,
        headers: headers,
        body: jsonEncode(data),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 401) {
        await clearToken(); // Effacer le token en cas d'erreur d'authentification
        throw Exception('Authentication failed');
      } else {
        print('HTTP Error: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to post data: ${response.statusCode}');
      }
    } catch (e) {
      print('Error in POST request: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final headers = await _getHeaders();
      
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: headers,
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 401) {
        await clearToken(); // Effacer le token en cas d'erreur d'authentification
        throw Exception('Authentication failed. Please login again.');
      } else {
        throw Exception('Failed to get current user: ${response.statusCode}');
      }
    } catch (e) {
      print('Error getting current user: $e');
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: <String, String>{
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: {
          'username': username,
          'password': password,
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        print('Login failed: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to login: ${response.statusCode}');
      }
    } on SocketException catch (e) {
      print('Connection error during login: $e');
      throw Exception('Connection failed. Please check if the server is running and accessible.');
    } on TimeoutException catch (e) {
      print('Timeout error during login: $e');
      throw Exception('Request timeout. Please check your internet connection.');
    } catch (e) {
      print('Login error: $e');
      throw Exception('Login failed: $e');
    }
  }

  Future<void> logout() async {
    try {
      final token = await getToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/auth/logout'),
        headers: await _getHeaders(),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode != 200) {
        throw Exception('Failed to logout: ${response.statusCode}');
      }

      // Supprimer le token localement
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('jwt_token');
      await prefs.remove('token');
      await prefs.remove('access_token');
    } catch (e) {
      print('Logout error: $e');
      throw Exception('Logout failed: $e');
    }
  }
}