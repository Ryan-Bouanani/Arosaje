import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/plant_care_advice.dart';
import 'api_service.dart';

class PlantCareAdviceService {
  final ApiService _apiService = ApiService();

  Future<AdviceStats> getAdviceStats() async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.get(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/stats'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return AdviceStats.fromJson(data);
      } else {
        throw Exception('Erreur lors du chargement des statistiques: ${response.statusCode}');
      }
    } catch (e) {
      print('Erreur getAdviceStats: $e');
      throw Exception('Erreur de connexion lors du chargement des statistiques');
    }
  }

  Future<List<PlantCareWithAdvice>> getPlantCaresToReview({
    AdvicePriority? priority,
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      String url = '${_apiService.baseUrl}/plant-care-advice/to-review?skip=$skip&limit=$limit';
      if (priority != null) {
        url += '&priority=${priority.value}';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => PlantCareWithAdvice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement des gardes à examiner: ${response.statusCode}');
      }
    } catch (e) {
      print('Erreur getPlantCaresToReview: $e');
      throw Exception('Erreur de connexion lors du chargement des gardes à examiner');
    }
  }

  Future<List<PlantCareWithAdvice>> getPlantCaresWithAdvice({
    ValidationStatus? validationStatus,
    bool myAdviceOnly = false,
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      String url = '${_apiService.baseUrl}/plant-care-advice/reviewed?skip=$skip&limit=$limit&my_advice_only=$myAdviceOnly';
      if (validationStatus != null) {
        url += '&validation_status=${validationStatus.value}';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => PlantCareWithAdvice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement des avis: ${response.statusCode}');
      }
    } catch (e) {
      print('Erreur getPlantCaresWithAdvice: $e');
      throw Exception('Erreur de connexion lors du chargement des avis');
    }
  }

  Future<PlantCareAdvice> createAdvice(PlantCareAdviceCreate adviceData) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.post(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: json.encode(adviceData.toJson()),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return PlantCareAdvice.fromJson(data);
      } else {
        final decodedBody = utf8.decode(response.bodyBytes);
        final errorData = json.decode(decodedBody);
        throw Exception(errorData['detail'] ?? 'Erreur lors de la création du conseil');
      }
    } catch (e) {
      print('Erreur createAdvice: $e');
      if (e.toString().contains('Exception:')) {
        rethrow;
      }
      throw Exception('Erreur de connexion lors de la création du conseil');
    }
  }

  Future<PlantCareAdvice> updateAdvice(int adviceId, Map<String, dynamic> updates) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.put(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/$adviceId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: json.encode(updates),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return PlantCareAdvice.fromJson(data);
      } else {
        final decodedBody = utf8.decode(response.bodyBytes);
        final errorData = json.decode(decodedBody);
        throw Exception(errorData['detail'] ?? 'Erreur lors de la mise à jour du conseil');
      }
    } catch (e) {
      print('Erreur updateAdvice: $e');
      if (e.toString().contains('Exception:')) {
        rethrow;
      }
      throw Exception('Erreur de connexion lors de la mise à jour du conseil');
    }
  }

  Future<PlantCareAdvice> validateAdvice(int adviceId, PlantCareAdviceValidation validation) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.post(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/$adviceId/validate'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: json.encode(validation.toJson()),
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return PlantCareAdvice.fromJson(data);
      } else {
        final decodedBody = utf8.decode(response.bodyBytes);
        final errorData = json.decode(decodedBody);
        throw Exception(errorData['detail'] ?? 'Erreur lors de la validation du conseil');
      }
    } catch (e) {
      print('Erreur validateAdvice: $e');
      if (e.toString().contains('Exception:')) {
        rethrow;
      }
      throw Exception('Erreur de connexion lors de la validation du conseil');
    }
  }

  Future<PlantCareAdvice> getAdviceById(int adviceId) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.get(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/$adviceId'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return PlantCareAdvice.fromJson(data);
      } else {
        throw Exception('Conseil non trouvé');
      }
    } catch (e) {
      print('Erreur getAdviceById: $e');
      throw Exception('Erreur de connexion lors de la récupération du conseil');
    }
  }

  Future<List<PlantCareAdvice>> getAdviceHistory(int plantCareId) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.get(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/plant-care/$plantCareId/history'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => PlantCareAdvice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement de l\'historique: ${response.statusCode}');
      }
    } catch (e) {
      print('Erreur getAdviceHistory: $e');
      throw Exception('Erreur de connexion lors du chargement de l\'historique');
    }
  }

  Future<List<PlantCareAdvice>> getCurrentAdvice(int plantCareId) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.get(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/plant-care/$plantCareId/current'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = json.decode(decodedBody);
        return data.map((item) => PlantCareAdvice.fromJson(item)).toList();
      } else {
        throw Exception('Erreur lors du chargement des conseils actuels: ${response.statusCode}');
      }
    } catch (e) {
      print('Erreur getCurrentAdvice: $e');
      throw Exception('Erreur de connexion lors du chargement des conseils actuels');
    }
  }

  Future<Map<String, dynamic>> getCountByPriority(AdvicePriority priority) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('Aucun token d\'authentification disponible');
      }

      final response = await http.get(
        Uri.parse('${_apiService.baseUrl}/plant-care-advice/priority/${priority.value}/count'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final data = json.decode(decodedBody);
        return {
          'priority': data['priority'] as String,
          'count': data['count'] as int
        };
      } else {
        throw Exception('Erreur lors du comptage: ${response.statusCode}');
      }
    } catch (e) {
      print('Erreur getCountByPriority: $e');
      return {'priority': priority.value, 'count': 0};
    }
  }
}