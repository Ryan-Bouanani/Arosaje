import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';
import 'dart:async';

class ApiService {
  // Pour WSL2, utilisez l'IP de l'hôte ou une IP accessible depuis l'émulateur
  static const String baseUrl = 'http://10.0.2.2:8000'; // Pour l'émulateur Android
  // Alternative: static const String baseUrl = 'http://192.168.1.100:8000'; // Remplacez par votre IP réseau

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    // Essayer plusieurs clés possibles pour le token
    String? token = prefs.getString('jwt_token') ?? 
                   prefs.getString('token') ?? 
                   prefs.getString('access_token');
    
    print('Token retrieved: ${token != null ? "Found (length: ${token.length})" : "Not found"}');
    return token;
  }

  Future<dynamic> get(String endpoint, {Map<String, dynamic>? queryParameters}) async {
    try {
      final token = await getToken();
      
      print('Making GET request to: $baseUrl$endpoint');
      print('Token present: ${token != null}');

      Map<String, String>? convertedParams;
      if (queryParameters != null) {
        convertedParams = queryParameters.map((key, value) => MapEntry(key, value.toString()));
      }
      
      final uri = Uri.parse('$baseUrl$endpoint').replace(queryParameters: convertedParams);
      
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };
      
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
      
      print('Request headers: $headers');
      
      final response = await http.get(
        uri,
        headers: headers,
      ).timeout(const Duration(seconds: 10));

      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 401) {
        throw Exception('Authentication failed. Please login again.');
      } else {
        print('HTTP Error: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to load data: ${response.statusCode}');
      }
    } on SocketException catch (e) {
      print('Connection error: $e');
      throw Exception('Connection failed. Please check if the server is running and accessible.');
    } on TimeoutException catch (e) {
      print('Timeout error: $e');
      throw Exception('Request timeout. Please check your internet connection.');
    } catch (e) {
      print('General error: $e');
      throw Exception('An error occurred: $e');
    }
  }

  Future<dynamic> post(String endpoint, dynamic data) async {
    try {
      final token = await getToken();
      final uri = Uri.parse('$baseUrl$endpoint');
      
      final response = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(data),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        print('HTTP Error: ${response.statusCode} - ${response.body}');
        throw Exception('Failed to post data: ${response.statusCode}');
      }
    } on SocketException catch (e) {
      print('Connection error: $e');
      throw Exception('Connection failed. Please check if the server is running and accessible.');
    } on TimeoutException catch (e) {
      print('Timeout error: $e');
      throw Exception('Request timeout. Please check your internet connection.');
    } catch (e) {
      print('General error: $e');
      throw Exception('An error occurred: $e');
    }
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final token = await getToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 401) {
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
}