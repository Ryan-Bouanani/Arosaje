import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_service.dart';

class ProfileService {
  final ApiService _apiService = ApiService();

  Future<bool> updateProfile({
    String? email,
    String? lastName,
    String? firstName,
    String? telephone,
    String? location,
  }) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Non authentifié');
      }

      Map<String, dynamic> data = {};
      if (email != null) data['email'] = email;
      if (lastName != null) data['last_name'] = lastName;
      if (firstName != null) data['first_name'] = firstName;
      if (telephone != null) data['telephone'] = telephone;
      if (location != null) data['location'] = location;

      final response = await http.put(
        Uri.parse('${_apiService.baseUrl}/auth/profile'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode(data),
      );

      if (response.statusCode == 200) {
        return true;
      } else if (response.statusCode == 400) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Erreur de mise à jour');
      } else {
        throw Exception('Erreur serveur: ${response.statusCode}');
      }
    } catch (e) {
      throw e;
    }
  }

  Future<bool> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Non authentifié');
      }

      final response = await http.post(
        Uri.parse('${_apiService.baseUrl}/auth/change-password'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'current_password': currentPassword,
          'new_password': newPassword,
        }),
      );

      if (response.statusCode == 200) {
        return true;
      } else if (response.statusCode == 400) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Erreur de changement de mot de passe');
      } else {
        throw Exception('Erreur serveur: ${response.statusCode}');
      }
    } catch (e) {
      throw e;
    }
  }
}
