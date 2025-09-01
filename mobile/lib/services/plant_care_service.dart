import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/services/storage_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class PlantCareService {
  final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://localhost:8000';
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
      Uri.parse('$baseUrl/plant-care/?as_owner=true'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      // Filtrer pour exclure les gardes terminées
      return jsonResponse
          .where((data) => data['status']?.toString().toLowerCase() != 'completed')
          .map((data) {
        if (data['plant'] != null && data['plant']['photo'] != null) {
          data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
        }
        return data as Map<String, dynamic>;
      }).toList();
    } else {
      throw Exception('Échec du chargement des gardes');
    }
  }

  Future<List<Map<String, dynamic>>> getMyCaretakingPlants() async {
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
      // Filtrer pour exclure les gardes terminées
      return jsonResponse
          .where((data) => data['status']?.toString().toLowerCase() != 'completed')
          .map((data) {
        if (data['plant'] != null && data['plant']['photo'] != null) {
          data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
        }
        return data as Map<String, dynamic>;
      }).toList();
    } else {
      throw Exception('Échec du chargement des gardes en tant que gardien');
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

  Future<Map<String, dynamic>> uploadBeforePhoto(int careId, String imagePath) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final uri = Uri.parse('$baseUrl/plant-care/$careId/before-photo');
    final request = http.MultipartRequest('POST', uri);
    
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('photo', imagePath));
    
    final response = await request.send();
    final responseData = await response.stream.bytesToString();
    
    if (response.statusCode == 200 || response.statusCode == 201) {
      return json.decode(responseData);
    } else {
      throw Exception('Échec de l\'upload de la photo avant garde');
    }
  }

  Future<Map<String, dynamic>> uploadAfterPhoto(int careId, String imagePath) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final uri = Uri.parse('$baseUrl/plant-care/$careId/after-photo');
    final request = http.MultipartRequest('POST', uri);
    
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('photo', imagePath));
    
    final response = await request.send();
    final responseData = await response.stream.bytesToString();
    
    if (response.statusCode == 200 || response.statusCode == 201) {
      return json.decode(responseData);
    } else {
      throw Exception('Échec de l\'upload de la photo après garde');
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

  Future<Map<String, dynamic>> completePlantCareByOwner(int careId) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.put(
      Uri.parse('$baseUrl/plant-care/$careId/complete'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else if (response.statusCode == 403) {
      throw Exception('Vous n\'êtes pas autorisé à terminer cette garde');
    } else if (response.statusCode == 400) {
      final errorData = json.decode(response.body);
      throw Exception(errorData['detail'] ?? 'Cette garde ne peut pas être terminée');
    } else {
      throw Exception('Échec de la fin de garde');
    }
  }

  // Méthodes pour l'historique des gardes terminées
  Future<List<Map<String, dynamic>>> getCompletedOwnedPlants() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/plant-care/?as_owner=true'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      // Filtrer pour inclure UNIQUEMENT les gardes terminées
      return jsonResponse
          .where((data) => data['status']?.toString().toLowerCase() == 'completed')
          .map((data) {
        if (data['plant'] != null && data['plant']['photo'] != null) {
          data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
        }
        return data as Map<String, dynamic>;
      }).toList();
    } else {
      throw Exception('Échec du chargement de l\'historique des plantes confiées');
    }
  }

  Future<List<Map<String, dynamic>>> getCompletedCaretakingPlants() async {
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
      // Filtrer pour inclure UNIQUEMENT les gardes terminées
      return jsonResponse
          .where((data) => data['status']?.toString().toLowerCase() == 'completed')
          .map((data) {
        if (data['plant'] != null && data['plant']['photo'] != null) {
          data['plant']['photo'] = _buildPhotoUrl(data['plant']['photo']);
        }
        return data as Map<String, dynamic>;
      }).toList();
    } else {
      throw Exception('Échec du chargement de l\'historique des gardes');
    }
  }
} 