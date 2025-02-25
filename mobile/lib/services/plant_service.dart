import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/models/plant.dart';
import 'package:mobile/services/storage_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class PlantService {
  final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://10.0.2.2:8000';
  late final StorageService _storageService;

  static Future<PlantService> init() async {
    final service = PlantService();
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

  Future<List<Plant>> getMyPlants() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plants/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) {
        // Construire l'URL complète pour la photo
        if (data['photo'] != null) {
          data['photo'] = _buildPhotoUrl(data['photo']);
        }
        return Plant.fromJson(data);
      }).toList();
    } else {
      throw Exception('Échec du chargement des plantes');
    }
  }

  Future<List<Plant>> getPlantsByOwner(int ownerId) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plants/?owner_id=$ownerId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) {
        // Construire l'URL complète pour la photo
        if (data['photo'] != null) {
          data['photo'] = _buildPhotoUrl(data['photo']);
        }
        return Plant.fromJson(data);
      }).toList();
    } else {
      throw Exception('Échec du chargement des plantes');
    }
  }
} 