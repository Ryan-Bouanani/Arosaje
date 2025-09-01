import 'dart:convert';
import 'dart:io' if (dart.library.html) 'dart:html' as io;
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:mobile/services/storage_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/foundation.dart';

class CareReportService {
  final String baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://localhost:8000';
  late final StorageService _storageService;

  static Future<CareReportService> init() async {
    final service = CareReportService();
    service._storageService = await StorageService.init();
    return service;
  }

  String _buildPhotoUrl(String? photoPath) {
    if (photoPath == null || photoPath.isEmpty) return '';
    // Si le chemin commence déjà par http, on le retourne tel quel
    if (photoPath.startsWith('http')) return photoPath;
    // Sinon on construit l'URL complète
    return '$baseUrl$photoPath';
  }

  Future<Map<String, dynamic>> createCareReport({
    required int plantCareId,
    required String healthLevel,
    required String hydrationLevel,
    required String vitalityLevel,
    String? description,
  }) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.post(
      Uri.parse('$baseUrl/care-reports/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'plant_care_id': plantCareId,
        'health_level': healthLevel,
        'hydration_level': hydrationLevel,
        'vitality_level': vitalityLevel,
        'description': description,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return json.decode(response.body);
    } else {
      throw Exception('Échec de la création du rapport: ${response.statusCode} - ${response.body}');
    }
  }

  Future<Map<String, dynamic>> uploadCareReportPhoto(int reportId, dynamic imageData) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final uri = Uri.parse('$baseUrl/care-reports/$reportId/photo');
    final request = http.MultipartRequest('POST', uri);
    
    request.headers['Authorization'] = 'Bearer $token';
    
    if (kIsWeb) {
      // Pour Flutter Web, imageData devrait être un Uint8List
      if (imageData is Uint8List) {
        request.files.add(http.MultipartFile.fromBytes(
          'photo',
          imageData,
          filename: 'photo.jpg',
        ));
      } else {
        throw Exception('Format d\'image non supporté pour le web');
      }
    } else {
      // Pour mobile, imageData devrait être un path (String)
      if (imageData is String) {
        request.files.add(await http.MultipartFile.fromPath('photo', imageData));
      } else {
        throw Exception('Format d\'image non supporté pour mobile');
      }
    }
    
    final response = await request.send();
    final responseData = await response.stream.bytesToString();
    
    if (response.statusCode == 200 || response.statusCode == 201) {
      return json.decode(responseData);
    } else {
      throw Exception('Échec de l\'upload de la photo: ${response.statusCode} - $responseData');
    }
  }

  Future<List<Map<String, dynamic>>> getCareReportsByPlantCare(int plantCareId) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/care-reports/plant-care/$plantCareId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) => data as Map<String, dynamic>).toList();
    } else {
      throw Exception('Échec du chargement des rapports');
    }
  }

  Future<List<Map<String, dynamic>>> getMyCareReports() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/care-reports/my-reports'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) => data as Map<String, dynamic>).toList();
    } else {
      throw Exception('Échec du chargement de mes rapports');
    }
  }

  Future<List<Map<String, dynamic>>> getCareReportsForBotanist({int skip = 0, int limit = 100}) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/care-reports/for-botanist?skip=$skip&limit=$limit'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) {
        final report = data as Map<String, dynamic>;
        if (report['photo_url'] != null) {
          report['photo_url'] = _buildPhotoUrl(report['photo_url']);
        }
        return report;
      }).toList();
    } else if (response.statusCode == 403) {
      throw Exception('Accès réservé aux botanistes');
    } else {
      throw Exception('Échec du chargement des rapports pour botanistes');
    }
  }

  Future<List<Map<String, dynamic>>> getCareReportsForMyPlants() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/care-reports/my-plants'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) => data as Map<String, dynamic>).toList();
    } else {
      throw Exception('Échec du chargement des rapports de mes plantes');
    }
  }

  Future<Map<String, dynamic>> addAdviceToReport(int reportId, String adviceText) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.post(
      Uri.parse('$baseUrl/botanist-advice/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'care_report_id': reportId,
        'advice_text': adviceText,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return json.decode(response.body);
    } else {
      throw Exception('Échec de l\'ajout de l\'avis: ${response.statusCode} - ${response.body}');
    }
  }

  Future<Map<String, dynamic>> updateAdviceToReport(int adviceId, String adviceText) async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.put(
      Uri.parse('$baseUrl/botanist-advice/$adviceId'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'advice_text': adviceText,
      }),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Échec de la modification de l\'avis: ${response.statusCode} - ${response.body}');
    }
  }

  Future<List<Map<String, dynamic>>> getMyAdvisedReports() async {
    final token = await _storageService.getToken();
    if (token == null) throw Exception('Non authentifié');

    final response = await http.get(
      Uri.parse('$baseUrl/care-reports/with-my-advice'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) {
        final report = data as Map<String, dynamic>;
        if (report['photo_url'] != null) {
          report['photo_url'] = _buildPhotoUrl(report['photo_url']);
        }
        return report;
      }).toList();
    } else if (response.statusCode == 403) {
      throw Exception('Accès réservé aux botanistes');
    } else {
      throw Exception('Échec du chargement de mes rapports commentés');
    }
  }
}