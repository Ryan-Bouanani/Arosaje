import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/services/storage_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dart:developer' as developer;
import '../models/advice.dart';

class UnifiedAdviceService {
  final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://localhost:8000';
  late final StorageService _storageService;

  static Future<UnifiedAdviceService> init() async {
    final service = UnifiedAdviceService();
    service._storageService = await StorageService.init();
    return service;
  }

  Future<String?> _getToken() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');
    return token;
  }

  Map<String, String> _getHeaders(String token) {
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json; charset=utf-8',
    };
  }

  // ===== STATISTIQUES =====
  
  Future<AdviceStats> getAdviceStats() async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final response = await http.get(
        Uri.parse('$baseUrl/advices/stats'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return AdviceStats.fromJson(data);
      } else {
        throw Exception('Erreur lors du chargement des statistiques: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur getAdviceStats: $e');
      throw Exception('Erreur de connexion lors du chargement des statistiques');
    }
  }

  // ===== GARDES À EXAMINER (Onglet "À examiner") =====

  Future<List<PlantCareWithAdvice>> getPlantCaresToReview({
    AdvicePriority? priority,
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      String url = '$baseUrl/advices/to-review?skip=$skip&limit=$limit';
      if (priority != null) {
        url += '&priority=${priority.value}';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => PlantCareWithAdvice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement des gardes à examiner: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur getPlantCaresToReview: $e');
      throw Exception('Erreur de connexion lors du chargement des gardes à examiner');
    }
  }

  // ===== GARDES AVEC AVIS (Onglet "Avis") =====

  Future<List<PlantCareWithAdvice>> getPlantCaresWithAdvice({
    ValidationStatus? validationStatus,
    bool myAdviceOnly = false,
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      String url = '$baseUrl/advices/reviewed?skip=$skip&limit=$limit&my_advice_only=$myAdviceOnly';
      if (validationStatus != null) {
        url += '&validation_status=${validationStatus.value}';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => PlantCareWithAdvice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement des gardes avec avis: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur getPlantCaresWithAdvice: $e');
      throw Exception('Erreur de connexion lors du chargement des gardes avec avis');
    }
  }

  // ===== CRÉATION D'AVIS =====

  Future<Advice> createAdvice({
    required int plantCareId,
    required String title,
    required String content,
    AdvicePriority priority = AdvicePriority.normal,
  }) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final response = await http.post(
        Uri.parse('$baseUrl/advices/'),
        headers: _getHeaders(token),
        body: json.encode({
          'plant_care_id': plantCareId,
          'title': title,
          'content': content,
          'priority': priority.value,
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return Advice.fromJson(data);
      } else {
        throw Exception('Erreur lors de la création de l\'avis: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur createAdvice: $e');
      throw Exception('Erreur lors de la création de l\'avis');
    }
  }

  // ===== MODIFICATION D'AVIS =====

  Future<Advice> updateAdvice({
    required int adviceId,
    String? title,
    String? content,
    AdvicePriority? priority,
  }) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final Map<String, dynamic> updateData = {};
      if (title != null) updateData['title'] = title;
      if (content != null) updateData['content'] = content;
      if (priority != null) updateData['priority'] = priority.value;

      final response = await http.put(
        Uri.parse('$baseUrl/advices/$adviceId'),
        headers: _getHeaders(token),
        body: json.encode(updateData),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return Advice.fromJson(data);
      } else {
        throw Exception('Erreur lors de la modification de l\'avis: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur updateAdvice: $e');
      throw Exception('Erreur lors de la modification de l\'avis');
    }
  }

  // ===== VALIDATION D'AVIS =====

  Future<Advice> validateAdvice({
    required int adviceId,
    required ValidationStatus validationStatus,
    String? validationComment,
  }) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final response = await http.post(
        Uri.parse('$baseUrl/advices/$adviceId/validate'),
        headers: _getHeaders(token),
        body: json.encode({
          'validation_status': validationStatus.value,
          'validation_comment': validationComment,
        }),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return Advice.fromJson(data);
      } else {
        throw Exception('Erreur lors de la validation de l\'avis: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur validateAdvice: $e');
      throw Exception('Erreur lors de la validation de l\'avis');
    }
  }

  // ===== SUPPRESSION D'AVIS =====

  Future<void> deleteAdvice(int adviceId) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final response = await http.delete(
        Uri.parse('$baseUrl/advices/$adviceId'),
        headers: _getHeaders(token),
      );

      if (response.statusCode != 204 && response.statusCode != 200) {
        throw Exception('Erreur lors de la suppression de l\'avis: ${response.statusCode}');
      }

      developer.log('Avis $adviceId supprimé avec succès');
    } catch (e) {
      developer.log('Erreur deleteAdvice: $e');
      throw Exception('Erreur lors de la suppression de l\'avis');
    }
  }

  // ===== RÉCUPÉRER DÉTAILS D'UNE GARDE =====

  Future<PlantCareWithAdvice?> getPlantCareDetails(int plantCareId) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final response = await http.get(
        Uri.parse('$baseUrl/advices/plant-care/$plantCareId/details'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return PlantCareWithAdvice.fromJson(data);
      } else if (response.statusCode == 404) {
        return null;
      } else {
        throw Exception('Erreur lors du chargement des détails: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur getPlantCareDetails: $e');
      throw Exception('Erreur lors du chargement des détails');
    }
  }

  // ===== RÉCUPÉRER CONSEILS D'UNE GARDE =====

  Future<List<Advice>> getCurrentAdvice(int plantCareId) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final response = await http.get(
        Uri.parse('$baseUrl/advices/plant-care/$plantCareId'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => Advice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement des conseils: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur getCurrentAdvice: $e');
      throw Exception('Erreur lors du chargement des conseils');
    }
  }

  // ===== RÉCUPÉRER HISTORIQUE D'UN AVIS =====

  Future<List<Advice>> getAdviceHistory(int adviceId) async {
    try {
      final token = await _getToken();
      if (token == null) throw Exception('Token requis');

      final response = await http.get(
        Uri.parse('$baseUrl/advices/$adviceId/history'),
        headers: _getHeaders(token),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => Advice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement de l\'historique: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('Erreur getAdviceHistory: $e');
      throw Exception('Erreur lors du chargement de l\'historique');
    }
  }
}
