import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/services/storage_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dart:developer' as developer;

class AdviceService {
  final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://10.0.2.2:8000';
  late final StorageService _storageService;

  static Future<AdviceService> init() async {
    final service = AdviceService();
    service._storageService = await StorageService.init();
    return service;
  }

  Future<List<Map<String, dynamic>>> getMyAdvices({int skip = 0, int limit = 100}) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/advices/botanist/me?skip=$skip&limit=$limit'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    developer.log('Status code: ${response.statusCode}');
    developer.log('Response body: ${response.body}');

    if (response.statusCode == 200) {
      final jsonResponse = json.decode(response.body);
      developer.log('JSON Response: $jsonResponse');
      
      if (jsonResponse == null) {
        developer.log('Response is null');
        return [];
      }

      if (!jsonResponse.containsKey('advices')) {
        developer.log('Response does not contain advices key');
        return [];
      }

      final List<dynamic> advices = jsonResponse['advices'] ?? [];
      developer.log('Nombre de conseils trouvés: ${advices.length}');
      
      return advices.map((data) {
        try {
          return <String, dynamic>{
            'id': data['id'] ?? 0,
            'texte': data['texte'] ?? '',
            'plant_id': data['plant_id'] ?? 0,
            'status': data['status'] ?? 'PENDING',
            'created_at': data['created_at'],
            'updated_at': data['updated_at'],
            'botanist_id': data['botanist_id'] ?? 0,
            'plant': data['plant'] ?? <String, dynamic>{},
          };
        } catch (e) {
          developer.log('Erreur lors du mapping d\'un conseil: $e');
          return <String, dynamic>{};
        }
      }).where((map) => map.isNotEmpty).toList();
    } else {
      developer.log('Erreur: ${response.statusCode} - ${response.body}');
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> getPendingAdviceRequests({int skip = 0, int limit = 100}) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    developer.log('Envoi de la requête getPendingAdviceRequests');
    developer.log('URL: $baseUrl/advices/pending-requests?skip=$skip&limit=$limit');

    final response = await http.get(
      Uri.parse('$baseUrl/advices/pending-requests?skip=$skip&limit=$limit'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    developer.log('Status code: ${response.statusCode}');
    developer.log('Response body: ${response.body}');

    if (response.statusCode == 200) {
      final jsonResponse = json.decode(response.body);
      developer.log('JSON Response: $jsonResponse');
      
      if (jsonResponse == null) {
        developer.log('Response is null');
        return [];
      }

      if (!jsonResponse.containsKey('advices')) {
        developer.log('Response does not contain advices key');
        return [];
      }

      final List<dynamic> advices = jsonResponse['advices'] ?? [];
      developer.log('Nombre de conseils en attente trouvés: ${advices.length}');
      
      return advices.map((data) {
        try {
          return <String, dynamic>{
            'id': data['id'] ?? 0,
            'texte': data['texte'] ?? '',
            'plant_id': data['plant_id'] ?? 0,
            'status': data['status'] ?? 'PENDING',
            'created_at': data['created_at'],
            'updated_at': data['updated_at'],
            'botanist_id': data['botanist_id'] ?? 0,
            'plant': data['plant'] ?? <String, dynamic>{},
          };
        } catch (e) {
          developer.log('Erreur lors du mapping d\'un conseil: $e');
          return <String, dynamic>{};
        }
      }).where((map) => map.isNotEmpty).toList();
    } else {
      developer.log('Erreur: ${response.statusCode} - ${response.body}');
      return [];
    }
  }

  Future<Map<String, dynamic>> createAdvice({
    required int plantId,
    required String texte,
  }) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    developer.log('Création d\'un nouveau conseil');
    developer.log('Plant ID: $plantId');

    final response = await http.post(
      Uri.parse('$baseUrl/advices/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'plant_id': plantId,
        'texte': texte,
      }),
    );

    developer.log('Status code: ${response.statusCode}');
    developer.log('Response body: ${response.body}');

    if (response.statusCode == 201 || response.statusCode == 200) {
      final jsonResponse = json.decode(response.body);
      developer.log('Conseil créé avec succès');
      return jsonResponse;
    } else {
      developer.log('Erreur lors de la création du conseil');
      throw Exception('Échec de la création du conseil');
    }
  }

  Future<void> deleteAdvice(int adviceId) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    developer.log('Suppression du conseil $adviceId');

    final response = await http.delete(
      Uri.parse('$baseUrl/advices/$adviceId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    developer.log('Status code: ${response.statusCode}');

    if (response.statusCode != 204 && response.statusCode != 200) {
      developer.log('Erreur lors de la suppression du conseil');
      throw Exception('Échec de la suppression du conseil');
    }
    
    developer.log('Conseil supprimé avec succès');
  }
} 