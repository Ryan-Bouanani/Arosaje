import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/services/storage_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class PlantCareService {
  final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://10.0.2.2:8000';
  late final StorageService _storageService;

  static Future<PlantCareService> init() async {
    final service = PlantCareService();
    service._storageService = await StorageService.init();
    return service;
  }

  String _buildPhotoUrl(String? photoPath) {
    if (photoPath == null) return '';
    // Si le chemin commence déjà par http, on le retourne tel quel
    if (photoPath.startsWith('http')) return photoPath;
    // Sinon on construit l'URL complète
    return '$baseUrl/$photoPath';
  }

  Future<Map<String, dynamic>> createPlantCare({
    required int plantId,
    required DateTime startDate,
    required DateTime endDate,
    required String localisation,
    String? careInstructions,
  }) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.post(
      Uri.parse('$baseUrl/plant-care/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'plant_id': plantId,
        'start_date': startDate.toIso8601String(),
        'end_date': endDate.toIso8601String(),
        'localisation': localisation,
        'care_instructions': careInstructions,
      }),
    );

    if (response.statusCode == 201 || response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Échec de la création de la garde: ${response.statusCode}');
    }
  }

  Future<List<Map<String, dynamic>>> getMyPlantCares() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plant-care/?as_caretaker=true'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) {
        if (data['plant'] != null && data['plant']['photo'] != null) {
          data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
        }
        return data as Map<String, dynamic>;
      }).toList();
    } else {
      throw Exception('Échec du chargement des gardes');
    }
  }

  Future<List<Map<String, dynamic>>> getPendingPlantCares() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plant-care/?status=pending&as_owner=false'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) {
        if (data['plant'] != null && data['plant']['photo'] != null) {
          data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
        }
        return data as Map<String, dynamic>;
      }).toList();
    } else {
      throw Exception('Échec du chargement des gardes en attente');
    }
  }

  Future<Map<String, dynamic>> getPlantCareDetails(int careId) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plant-care/$careId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['plant'] != null && data['plant']['photo'] != null) {
        data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
      }
      return data;
    } else {
      throw Exception('Échec du chargement des détails de la garde');
    }
  }

  Future<Map<String, dynamic>> acceptPlantCare(int careId) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.put(
      Uri.parse('$baseUrl/plant-care/$careId/status'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'status': 'accepted'
      }),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Échec de l\'acceptation de la garde');
    }
  }

  Future<Map<String, dynamic>> getPlantCareDetailsByPlantId(int plantId) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plant-care/by-plant/$plantId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['plant'] != null && data['plant']['photo'] != null) {
        data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
      }
      return data;
    } else {
      throw Exception('Échec du chargement des détails de la garde pour cette plante');
    }
  }
} 