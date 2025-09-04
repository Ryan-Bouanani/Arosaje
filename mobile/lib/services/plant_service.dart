import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:mobile/models/plant.dart';
import 'package:mobile/services/storage_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

// Import conditionnel pour File (éviter sur web)
import 'dart:io' if (dart.library.html) 'dart:io' show File;

class PlantService {
  final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://localhost:8000';
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

  Future<Plant> createPlant({
    required String nom,
    String? espece,
    dynamic imageFile, // File sur mobile
    Uint8List? webImage, // Bytes sur web
    String? originalFileName, // Nom original avec extension
  }) async {
    final token = _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/plants/'),
    );

    request.headers.addAll({
      'Authorization': 'Bearer $token',
    });

    request.fields['nom'] = nom;
    if (espece != null) request.fields['espece'] = espece;

    if (kIsWeb && webImage != null) {
      request.files.add(http.MultipartFile.fromBytes(
        'photo',
        webImage,
        filename: originalFileName ?? 'photo.jpg',
      ));
    } else if (!kIsWeb && imageFile != null) {
      request.files.add(await http.MultipartFile.fromPath(
        'photo',
        (imageFile as File).path,
      ));
    }

    final response = await request.send();
    final responseString = await response.stream.bytesToString();

    if (response.statusCode == 201 || response.statusCode == 200) {
      final data = json.decode(responseString);
      if (data['photo'] != null) {
        data['photo'] = _buildPhotoUrl(data['photo']);
      }
      return Plant.fromJson(data);
    } else {
      throw Exception('Échec de la création de la plante: ${response.statusCode}');
    }
  }

  Future<List<Plant>> getMyPlants() async {
    final token = _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plants/?owner_id=${await _storageService.getUserId()}'),
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
    final token = _storageService.getToken();
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

  Future<List<Plant>> getAllPlants() async {
    final token = _storageService.getToken();
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
        if (data['photo'] != null) {
          data['photo'] = _buildPhotoUrl(data['photo']);
        }
        return Plant.fromJson(data);
      }).toList();
    } else {
      throw Exception('Échec du chargement des plantes');
    }
  }

  Future<Plant> getPlantDetails(int plantId) async {
    final token = _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plants/$plantId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['photo'] != null) {
        data['photo'] = _buildPhotoUrl(data['photo']);
      }
      return Plant.fromJson(data);
    } else {
      throw Exception('Échec du chargement des détails de la plante');
    }
  }

  Future<Map<String, dynamic>> updatePlant({
    required int plantId,
    String? nom,
  }) async {
    final token = _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final Map<String, dynamic> updateData = {};
    if (nom != null) updateData['nom'] = nom;

    final response = await http.put(
      Uri.parse('$baseUrl/plants/$plantId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode(updateData),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['photo'] != null) {
        data['photo'] = _buildPhotoUrl(data['photo']);
      }
      return data;
    } else {
      throw Exception('Échec de la mise à jour de la plante: ${response.statusCode} - ${response.body}');
    }
  }
} 
