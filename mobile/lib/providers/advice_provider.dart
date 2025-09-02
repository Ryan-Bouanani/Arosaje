import 'package:flutter/foundation.dart';
import '../models/advice.dart';
import '../services/unified_advice_service.dart';
import '../services/auth_service.dart';
import '../services/storage_service.dart';

class AdviceProvider extends ChangeNotifier {
  UnifiedAdviceService? _service;
  bool _serviceInitialized = false;
  
  int? _currentBotanistId;

  // État des données
  List<PlantCareWithAdvice> _plantCaresToReview = [];
  List<PlantCareWithAdvice> _plantCaresWithAdvice = [];
  AdviceStats? _stats;

  // État de chargement
  bool _isLoadingToReview = false;
  bool _isLoadingReviewed = false;
  bool _isLoadingStats = false;

  // Filtres
  ValidationFilter _validationFilter = ValidationFilter.all;
  bool _myAdviceOnly = false; // Par défaut, afficher tous les avis dans l'onglet Avis

  // Erreurs
  String? _error;

  // Getters
  List<PlantCareWithAdvice> get plantCaresToReview => _plantCaresToReview;
  List<PlantCareWithAdvice> get plantCaresWithAdvice => _plantCaresWithAdvice;
  AdviceStats? get stats => _stats;
  
  bool get isLoadingToReview => _isLoadingToReview;
  bool get isLoadingReviewed => _isLoadingReviewed;
  bool get isLoadingStats => _isLoadingStats;
  
  ValidationFilter get validationFilter => _validationFilter;
  bool get myAdviceOnly => _myAdviceOnly;
  
  String? get error => _error;
  int? get currentBotanistId => _currentBotanistId;

  // Initialisation du service
  Future<void> initService() async {
    if (!_serviceInitialized) {
      _service = await UnifiedAdviceService.init();
      _serviceInitialized = true;
    }
  }

  // Charger l'ID du botaniste connecté
  Future<void> loadCurrentBotanistId() async {
    try {
      // S'assurer que le service est initialisé
      await initService();
      
      final storageService = await StorageService.init();
      final token = await storageService.getToken();
      if (token != null) {
        final authService = await AuthService.getInstance();
        final userData = await authService.getCurrentUser(token);
        _currentBotanistId = userData['id'];
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Erreur lors du chargement de l\'ID botaniste: $e');
    }
  }

  // Charger les statistiques
  Future<void> loadStats() async {
    _isLoadingStats = true;
    _error = null;
    notifyListeners();

    try {
      // S'assurer que le service est initialisé
      await initService();
      _stats = await _service!.getAdviceStats();
    } catch (e) {
      _error = 'Erreur lors du chargement des statistiques: $e';
      debugPrint('Error loading stats: $e');
    } finally {
      _isLoadingStats = false;
      notifyListeners();
    }
  }

  // Charger les gardes à examiner
  Future<void> loadPlantCaresToReview() async {
    _isLoadingToReview = true;
    _error = null;
    notifyListeners();

    try {
      // S'assurer que le service est initialisé
      await initService();
      _plantCaresToReview = await _service!.getPlantCaresToReview();
      
      // Trier par priorité (urgent en premier)
      _plantCaresToReview.sort((a, b) {
        if (a.priority == AdvicePriority.urgent && b.priority != AdvicePriority.urgent) {
          return -1;
        } else if (a.priority != AdvicePriority.urgent && b.priority == AdvicePriority.urgent) {
          return 1;
        } else if (a.priority == AdvicePriority.followUp && b.priority == AdvicePriority.normal) {
          return -1;
        } else if (a.priority == AdvicePriority.normal && b.priority == AdvicePriority.followUp) {
          return 1;
        }
        return 0;
      });
      
    } catch (e) {
      _error = 'Erreur lors du chargement des gardes à examiner: $e';
      debugPrint('Error loading plant cares to review: $e');
    } finally {
      _isLoadingToReview = false;
      notifyListeners();
    }
  }

  // Charger les gardes avec avis
  Future<void> loadPlantCaresWithAdvice() async {
    _isLoadingReviewed = true;
    _error = null;
    notifyListeners();

    try {
      // S'assurer que le service est initialisé
      await initService();
      ValidationStatus? statusFilter;
      switch (_validationFilter) {
        case ValidationFilter.pending:
          statusFilter = ValidationStatus.pending;
          break;
        case ValidationFilter.validated:
          statusFilter = ValidationStatus.validated;
          break;
        case ValidationFilter.rejected:
          statusFilter = ValidationStatus.rejected;
          break;
        case ValidationFilter.needsRevision:
          statusFilter = ValidationStatus.needsRevision;
          break;
        case ValidationFilter.all:
          statusFilter = null;
          break;
      }

      _plantCaresWithAdvice = await _service!.getPlantCaresWithAdvice(
        validationStatus: statusFilter,
        myAdviceOnly: _myAdviceOnly,
      );
      
    } catch (e) {
      _error = 'Erreur lors du chargement des avis: $e';
      debugPrint('Error loading plant cares with advice: $e');
    } finally {
      _isLoadingReviewed = false;
      notifyListeners();
    }
  }

  // Créer un nouveau conseil
  Future<Advice?> createAdvice({required int plantCareId, required String title, required String content, AdvicePriority priority = AdvicePriority.normal}) async {
    try {
      final advice = await _service!.createAdvice(plantCareId: plantCareId, title: title, content: content, priority: priority);
      
      // Recharger les données
      await loadPlantCaresToReview();
      await loadPlantCaresWithAdvice();
      await loadStats();
      
      return advice;
    } catch (e) {
      _error = 'Erreur lors de la création du conseil: $e';
      debugPrint('Error creating advice: $e');
      notifyListeners();
      return null;
    }
  }


  // Valider un conseil
  Future<Advice?> validateAdvice(
    int adviceId,
    ValidationStatus status,
    String? comment,
  ) async {
    try {
      final advice = await _service!.validateAdvice(adviceId: adviceId, validationStatus: status, validationComment: comment);
      
      // Recharger les données
      await loadPlantCaresWithAdvice();
      await loadStats();
      
      return advice;
    } catch (e) {
      _error = 'Erreur lors de la validation: $e';
      debugPrint('Error validating advice: $e');
      notifyListeners();
      return null;
    }
  }

  // Changer le filtre de validation
  void setValidationFilter(ValidationFilter filter) {
    if (_validationFilter != filter) {
      _validationFilter = filter;
      loadPlantCaresWithAdvice();
    }
  }

  // Basculer le filtre "Mes avis uniquement"
  void toggleMyAdviceOnly(bool value) {
    if (_myAdviceOnly != value) {
      _myAdviceOnly = value;
      loadPlantCaresWithAdvice();
    }
  }

  // Obtenir l'historique d'un conseil
  Future<List<Advice>> getAdviceHistory(int plantCareId) async {
    try {
      return await _service!.getAdviceHistory(plantCareId);
    } catch (e) {
      debugPrint('Error loading advice history: $e');
      return [];
    }
  }

  // Rafraîchir toutes les données
  Future<void> refresh() async {
    await Future.wait([
      loadStats(),
      loadPlantCaresToReview(),
      loadPlantCaresWithAdvice(),
    ]);
  }

  // Effacer l'erreur
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
