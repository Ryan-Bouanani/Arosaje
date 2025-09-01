import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:mobile/views/add_report_screen.dart';
import 'package:mobile/views/chat_list_screen.dart';
import 'package:mobile/views/chat_screen.dart';
import 'package:mobile/services/plant_care_service.dart';
import 'package:mobile/services/message_service.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/services/care_report_service.dart';
import 'package:mobile/services/user_service.dart';
import 'package:mobile/services/plant_care_advice_service.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/models/plant_care_advice.dart';
import 'package:mobile/widgets/image_zoom_dialog.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class PlantCareDetailsScreen extends StatefulWidget {
  final bool isCurrentPlant;
  final int? careId;
  final int? plantId;

  const PlantCareDetailsScreen({
    super.key,
    required this.isCurrentPlant,
    this.careId,
    this.plantId,
  }) : assert(careId != null || plantId != null, 'Either careId or plantId must be provided');

  @override
  State<PlantCareDetailsScreen> createState() => _PlantCareDetailsScreenState();
}

class _PlantCareDetailsScreenState extends State<PlantCareDetailsScreen> {
  late final PlantCareService _plantCareService;
  late final CareReportService _careReportService;
  late final UserService _userService;
  late final PlantCareAdviceService _plantCareAdviceService;
  late final PlantService _plantService;
  Map<String, dynamic>? _careDetails;
  List<Map<String, dynamic>> _careReports = [];
  List<PlantCareAdvice> _plantAdvices = [];
  bool _isLoading = true;
  bool _isLoadingReports = false;
  bool _isLoadingAdvices = false;
  String? _error;
  final ImagePicker _picker = ImagePicker();
  int? _currentUserId;
  bool _isEditMode = false;
  final TextEditingController _instructionsController = TextEditingController();
  final TextEditingController _plantNameController = TextEditingController();
  final TextEditingController _locationController = TextEditingController();
  dynamic _newPlantImage;

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  @override
  void dispose() {
    _instructionsController.dispose();
    _plantNameController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  Future<void> _initializeService() async {
    try {
      _plantCareService = await PlantCareService.init();
      _careReportService = await CareReportService.init();
      _userService = UserService(ApiService());
      _plantCareAdviceService = PlantCareAdviceService();
      _plantService = await PlantService.init();
      
      // Récupérer l'ID de l'utilisateur actuel
      _currentUserId = await _userService.getCurrentUserId();
      
      await _loadCareDetails();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadCareDetails() async {
    try {
      final details = widget.careId != null 
          ? await _plantCareService.getPlantCareDetails(widget.careId!)
          : await _plantCareService.getPlantCareDetailsByPlantId(widget.plantId!);
      
      
      setState(() {
        _careDetails = details;
        _isLoading = false;
        
        // Initialiser les contrôleurs avec les données actuelles
        _instructionsController.text = details['care_instructions'] ?? '';
        _plantNameController.text = details['plant']?['nom'] ?? '';
        _locationController.text = details['localisation'] ?? '';
      });
      
      // Charger les rapports de garde si on a les détails
      if (details['id'] != null) {
        await _loadCareReports();
      }
      
      // Charger les conseils pour la plante
      if (details['plant']?['id'] != null) {
        await _loadPlantAdvices();
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadCareReports() async {
    if (_careDetails?['id'] == null) return;
    
    try {
      setState(() {
        _isLoadingReports = true;
      });
      
      final reports = await _careReportService.getCareReportsByPlantCare(_careDetails!['id']);
      
      setState(() {
        _careReports = reports;
        _isLoadingReports = false;
      });
    } catch (e) {
      print('Erreur lors du chargement des rapports: $e');
      setState(() {
        _careReports = [];
        _isLoadingReports = false;
      });
    }
  }

  Future<void> _acceptCare() async {
    try {
      setState(() => _isLoading = true);
      if (widget.careId == null) {
        throw Exception('Cannot accept care without a care ID');
      }
      await _plantCareService.acceptPlantCare(widget.careId!);
      await _loadCareDetails(); // Recharger pour avoir le nouveau statut
      setState(() => _isLoading = false);
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _completeCare() async {
    // Demander confirmation
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Terminer la garde'),
          content: const Text('Êtes-vous sûr de vouloir terminer cette garde ? Cette action est irréversible.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Annuler'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: const Text('Terminer', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;

    try {
      setState(() => _isLoading = true);
      if (widget.careId == null) {
        throw Exception('Cannot complete care without a care ID');
      }
      
      await _plantCareService.completePlantCareByOwner(widget.careId!);
      await _loadCareDetails(); // Recharger pour avoir le nouveau statut
      
      setState(() => _isLoading = false);
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Garde terminée avec succès !'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _takeBeforePhoto() async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: kIsWeb ? ImageSource.gallery : ImageSource.camera,
        imageQuality: 80,
      );
      
      if (photo != null && widget.careId != null) {
        setState(() => _isLoading = true);
        
        await _plantCareService.uploadBeforePhoto(widget.careId!, photo.path);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Photo avant garde envoyée avec succès')),
        );
        
        await _loadCareDetails(); // Recharger pour avoir le nouveau statut
        setState(() => _isLoading = false);
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: ${e.toString()}')),
      );
    }
  }

  Future<void> _takeAfterPhoto() async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: kIsWeb ? ImageSource.gallery : ImageSource.camera,
        imageQuality: 80,
      );
      
      if (photo != null && widget.careId != null) {
        setState(() => _isLoading = true);
        
        await _plantCareService.uploadAfterPhoto(widget.careId!, photo.path);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Photo après garde envoyée. Garde terminée!')),
        );
        
        Navigator.pop(context, true); // Retour avec succès
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: ${e.toString()}')),
      );
    }
  }

  Future<void> _requestBotanistAdvice() async {
    try {
      if (_careDetails == null || _careDetails!['plant'] == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Informations de la plante non disponibles')),
        );
        return;
      }

      // Afficher une confirmation avant de créer la conversation
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: const Text('Demander un conseil'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Demander un conseil pour cette ${_careDetails!['plant']['nom']} ?'),
                const SizedBox(height: 16),
                const Text(
                  'Une conversation sera créée avec un botaniste pour vous aider.',
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Annuler'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Confirmer'),
              ),
            ],
          );
        },
      );

      if (confirmed == true) {
        // Créer la conversation avec un botaniste
        final messageService = MessageService(ApiService());
        final plantId = _careDetails!['plant']['id'];
        
        await messageService.createBotanistConversation(plantId);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Conversation créée avec un botaniste ! Allez dans la messagerie.'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Navigation vers la messagerie
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const ChatMenuScreen(),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur lors de la création de la conversation: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _contactOwner() async {
    try {
      if (_careDetails?['owner']?['nom'] == null || _careDetails?['owner']?['prenom'] == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Impossible de contacter le propriétaire')),
        );
        return;
      }

      // Navigation directe vers la page des messages
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => const ChatMenuScreen(),
        ),
      );
      
      // Afficher un message informatif
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Messagerie ouverte - Vous pourrez contacter ${_careDetails!['owner']['prenom']} ${_careDetails!['owner']['nom']}'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: ${e.toString()}')),
      );
    }
  }

  Future<void> _contactCaretaker() async {
    try {
      if (_careDetails?['caretaker']?['nom'] == null || _careDetails?['caretaker']?['prenom'] == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Impossible de contacter le gardien')),
        );
        return;
      }

      // Navigation directe vers la page des messages
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => const ChatMenuScreen(),
        ),
      );
      
      // Afficher un message informatif
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Messagerie ouverte - Vous pourrez contacter ${_careDetails!['caretaker']['prenom']} ${_careDetails!['caretaker']['nom']}'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: ${e.toString()}')),
      );
    }
  }

  Future<void> _loadPlantAdvices() async {
    if (widget.careId == null) return;
    
    try {
      setState(() {
        _isLoadingAdvices = true;
      });
      
      final advices = await _plantCareAdviceService.getCurrentAdvice(widget.careId!);
      
      setState(() {
        _plantAdvices = advices;
        _isLoadingAdvices = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingAdvices = false;
      });
      print('Erreur lors du chargement des conseils: $e');
    }
  }

  String _getOwnerDisplayName() {
    if (_careDetails?['owner'] == null) {
      return 'Propriétaire inconnu';
    }
    
    final ownerId = _careDetails!['owner']['id'];
    if (_currentUserId != null && ownerId == _currentUserId) {
      return 'Moi';
    }
    
    return '${_careDetails!['owner']['prenom']} ${_careDetails!['owner']['nom']}';
  }

  Color _getPriorityColor(AdvicePriority priority) {
    switch (priority) {
      case AdvicePriority.normal:
        return Colors.green;
      case AdvicePriority.urgent:
        return Colors.red;
      case AdvicePriority.followUp:
        return Colors.orange;
    }
  }

  bool _isCurrentUserOwner() {
    if (_careDetails?['owner'] == null || _currentUserId == null) {
      return false;
    }
    return _careDetails!['owner']['id'].toString() == _currentUserId.toString();
  }

  bool _canRequestBotanistAdvice() {
    if (_careDetails == null || _currentUserId == null) {
      return false;
    }
    
    // Vérifier le statut de la garde (doit être acceptée ou en cours)
    final status = _careDetails!['status']?.toString().toLowerCase();
    final isStatusValid = status == 'accepted' || status == 'in_progress';
    
    if (!isStatusValid) {
      return false;
    }
    
    // Vérifier si l'utilisateur est le propriétaire
    final isOwner = _careDetails!['owner_id'].toString() == _currentUserId.toString();
    
    // Vérifier si l'utilisateur est le gardien assigné
    final isAssignedCaretaker = _careDetails!['caretaker_id'] != null && 
                                 _careDetails!['caretaker_id'].toString() == _currentUserId.toString();
    
    // Retourner true si l'utilisateur est soit le propriétaire soit le gardien assigné
    return isOwner || isAssignedCaretaker;
  }

  String _formatDate(String? dateString) {
    if (dateString == null) return '';
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return dateString;
    }
  }

  bool _isInCarePeriod() {
    if (_careDetails?['start_date'] == null || _careDetails?['end_date'] == null) {
      return false;
    }
    
    try {
      final now = DateTime.now();
      final startDate = DateTime.parse(_careDetails!['start_date']);
      final endDate = DateTime.parse(_careDetails!['end_date']);
      
      // Vérifier si nous sommes dans la période de garde (inclus les dates de début/fin)
      return now.isAfter(startDate.subtract(const Duration(days: 1))) && 
             now.isBefore(endDate.add(const Duration(days: 1)));
    } catch (e) {
      return false;
    }
  }

  bool _hasCareStarted() {
    if (_careDetails?['start_date'] == null) {
      return false;
    }
    
    try {
      final now = DateTime.now();
      final startDate = DateTime.parse(_careDetails!['start_date']);
      
      // Vérifier si la garde a commencé (on est après ou égal à la date de début)
      // On compare seulement les dates, pas les heures
      final nowDate = DateTime(now.year, now.month, now.day);
      final startDateOnly = DateTime(startDate.year, startDate.month, startDate.day);
      
      return nowDate.isAfter(startDateOnly) || nowDate.isAtSameMomentAs(startDateOnly);
    } catch (e) {
      return false;
    }
  }

  void _toggleEditMode() {
    setState(() {
      _isEditMode = !_isEditMode;
      if (!_isEditMode) {
        // Annuler les modifications - restaurer les valeurs originales
        _instructionsController.text = _careDetails!['care_instructions'] ?? '';
        _plantNameController.text = _careDetails!['plant']?['nom'] ?? '';
        _locationController.text = _careDetails!['localisation'] ?? '';
        _newPlantImage = null;
      }
    });
  }

  Future<void> _saveChanges() async {
    try {
      // Sauvegarder le nom de la plante si modifié
      final plantId = _careDetails!['plant']['id'];
      final currentPlantName = _careDetails!['plant']['nom'];
      final newPlantName = _plantNameController.text.trim();
      
      if (newPlantName.isNotEmpty && newPlantName != currentPlantName) {
        await _plantService.updatePlant(
          plantId: plantId,
          nom: newPlantName,
        );
      }
      
      setState(() {
        _isEditMode = false;
        // Mettre à jour les détails avec les nouvelles valeurs sauvegardées
        _careDetails!['care_instructions'] = _instructionsController.text;
        _careDetails!['plant']['nom'] = newPlantName;
        _careDetails!['localisation'] = _locationController.text;
        // La photo sera gérée séparément si une nouvelle image est sélectionnée
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Modifications sauvegardées avec succès!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      setState(() {
        _isEditMode = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur lors de la sauvegarde: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _selectPlantImage() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() {
          _newPlantImage = image;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur lors de la sélection de l\'image: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Widget _buildAdviceCard(PlantCareAdvice advice) {
    final createdAt = advice.createdAt;
    final priority = advice.priority;
    final botanistName = advice.botanist?.fullName ?? 'Botaniste inconnu';
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // En-tête avec botaniste et date
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.eco, color: Colors.green, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Conseil de $botanistName',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                Text(
                  '${createdAt.day}/${createdAt.month}/${createdAt.year}',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // Statut du conseil
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: _getPriorityColor(priority).withOpacity(0.1),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                  color: _getPriorityColor(priority),
                ),
              ),
              child: Text(
                priority.displayName,
                style: TextStyle(
                  color: _getPriorityColor(priority),
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            
            const SizedBox(height: 12),
            
            // Texte du conseil
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                advice.content,
                style: const TextStyle(fontSize: 14),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCareReportCard(Map<String, dynamic> report) {
    final sessionDate = DateTime.tryParse(report['session_date'] ?? '');
    final photoUrl = report['photo_url'];
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // En-tête avec date et gardien
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.assignment_turned_in, color: Colors.green, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Séance d\'entretien',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                if (sessionDate != null)
                  Text(
                    '${sessionDate.day}/${sessionDate.month}/${sessionDate.year}',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // État de santé de la plante
            Row(
              children: [
                _buildHealthIndicator('Santé', report['health_level'] ?? 'N/A'),
                const SizedBox(width: 16),
                _buildHealthIndicator('Hydratation', report['hydration_level'] ?? 'N/A'),
                const SizedBox(width: 16),
                _buildHealthIndicator('Vitalité', report['vitality_level'] ?? 'N/A'),
              ],
            ),
            
            // Description si disponible
            if (report['description'] != null && report['description'].toString().isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.note, color: Colors.blue, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        report['description'],
                        style: const TextStyle(fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            
            // Photo si disponible
            if (photoUrl != null && photoUrl.toString().isNotEmpty) ...[
              const SizedBox(height: 12),
              GestureDetector(
                onTap: () {
                  ImageZoomDialog.show(
                    context,
                    'http://localhost:8000$photoUrl',
                    title: 'Photo de la séance d\'entretien',
                  );
                },
                child: Stack(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.network(
                        'http://localhost:8000$photoUrl', // URL complète
                        height: 150,
                        width: double.infinity,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            height: 150,
                            color: Colors.grey[200],
                            child: const Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.broken_image, color: Colors.grey),
                                  Text('Image non disponible', style: TextStyle(color: Colors.grey, fontSize: 12)),
                                ],
                              ),
                            ),
                          );
                        },
                        loadingBuilder: (context, child, loadingProgress) {
                          if (loadingProgress == null) return child;
                          return Container(
                            height: 150,
                            child: const Center(child: CircularProgressIndicator()),
                          );
                        },
                      ),
                    ),
                    // Indicateur de zoom
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.6),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Icon(
                          Icons.zoom_in,
                          color: Colors.white,
                          size: 16,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            
            // Avis botanistes si disponibles
            if (report['botanist_advices'] != null && 
                report['botanist_advices'] is List && 
                (report['botanist_advices'] as List).isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green[50],
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: Colors.green.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.local_florist, color: Colors.green, size: 16),
                        const SizedBox(width: 8),
                        const Text(
                          'Avis botaniste',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ...((report['botanist_advices'] as List).map((advice) => Container(
                      margin: const EdgeInsets.only(bottom: 6),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            advice['advice_text'] ?? '',
                            style: const TextStyle(fontSize: 13),
                          ),
                          if (advice['botanist'] != null) ...[
                            const SizedBox(height: 4),
                            Text(
                              '— ${advice['botanist']['prenom']} ${advice['botanist']['nom'] ?? ''}',
                              style: TextStyle(
                                fontSize: 11,
                                color: Colors.green[700],
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ],
                        ],
                      ),
                    )).toList()),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildHealthIndicator(String label, String level) {
    Color color;
    switch (level.toLowerCase()) {
      case 'bon':
        color = Colors.green;
        break;
      case 'moyen':
        color = Colors.orange;
        break;
      case 'bas':
        color = Colors.red;
        break;
      default:
        color = Colors.grey;
    }
    
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 4),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Text(
            level,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
          color: Colors.black,
        ),
        title: Text(
          _careDetails != null ? _careDetails!['plant']['nom'] : 'Chargement...',
          style: const TextStyle(color: Colors.black, fontSize: 18),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
        actions: [
          if (_careDetails != null && _isCurrentUserOwner())
            IconButton(
              icon: Icon(_isEditMode ? Icons.save : Icons.edit),
              onPressed: _isEditMode ? _saveChanges : _toggleEditMode,
              color: _isEditMode ? Colors.green : Colors.black,
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : SingleChildScrollView(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Owner Section
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const CircleAvatar(
                              backgroundColor: Colors.grey,
                              child: Icon(Icons.person, color: Colors.white),
                            ),
                            const SizedBox(width: 16),
                            Text(
                              _getOwnerDisplayName(),
                              style: const TextStyle(fontSize: 14),
                            ),
                          ],
                        ),

                        const SizedBox(height: 16),

                        // Caretaker Section (visible pour le propriétaire quand un gardien est assigné)
                        if (_isCurrentUserOwner() && _careDetails!['caretaker'] != null)
                          Column(
                            children: [
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  CircleAvatar(
                                    backgroundColor: Colors.green[700],
                                    child: const Icon(Icons.eco, color: Colors.white),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          'Gardien assigné',
                                          style: TextStyle(
                                            fontSize: 12,
                                            color: Colors.grey,
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                        const SizedBox(height: 2),
                                        Text(
                                          '${_careDetails!['caretaker']['prenom'] ?? ''} ${_careDetails!['caretaker']['nom'] ?? ''}',
                                          style: const TextStyle(
                                            fontSize: 14,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        if (_careDetails!['caretaker']['localisation'] != null)
                                          Text(
                                            _careDetails!['caretaker']['localisation'],
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: Colors.grey[600],
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                            ],
                          ),

                        // Période de garde
                        if (_careDetails!['start_date'] != null && _careDetails!['end_date'] != null)
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.blue[50],
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.blue[100]!),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.calendar_today, color: Colors.blue, size: 20),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'Période de garde',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          color: Colors.blue,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        'Du ${_formatDate(_careDetails!['start_date'])} au ${_formatDate(_careDetails!['end_date'])}',
                                        style: const TextStyle(fontSize: 14),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),

                        const SizedBox(height: 16),

                        // Action Buttons
                        if (_canRequestBotanistAdvice() || !_isCurrentUserOwner() || (_isCurrentUserOwner() && _careDetails!['caretaker'] != null))
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              if (_canRequestBotanistAdvice())
                                Expanded(
                                  child: OutlinedButton.icon(
                                    onPressed: _requestBotanistAdvice,
                                    icon: const Icon(Icons.local_florist, color: Colors.green),
                                    label: const Text(
                                      'Demander un conseil botaniste',
                                      textAlign: TextAlign.center,
                                      style: TextStyle(fontSize: 12),
                                    ),
                                    style: OutlinedButton.styleFrom(
                                      padding: const EdgeInsets.all(12),
                                    ),
                                  ),
                                ),
                              if (_canRequestBotanistAdvice() && (!_isCurrentUserOwner() || (_isCurrentUserOwner() && _careDetails!['caretaker'] != null)))
                                const SizedBox(width: 8),
                              if (!_isCurrentUserOwner())
                                Expanded(
                                  child: OutlinedButton.icon(
                                    onPressed: _isLoading ? null : _contactOwner,
                                    icon: const Icon(Icons.message, color: Colors.black),
                                  label: const Text(
                                    'Contacter le propriétaire',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(fontSize: 12),
                                  ),
                                  style: OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.all(12),
                                  ),
                                ),
                              ),
                              if (_isCurrentUserOwner() && _careDetails!['caretaker'] != null)
                                Expanded(
                                  child: OutlinedButton.icon(
                                    onPressed: _isLoading ? null : _contactCaretaker,
                                    icon: const Icon(Icons.message, color: Colors.black),
                                  label: const Text(
                                    'Contacter le gardien',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(fontSize: 12),
                                  ),
                                  style: OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.all(12),
                                  ),
                                ),
                              ),
                          ],
                        ),

                        // Status display only
                        if (_careDetails != null && _careDetails!['status'] != null) ...[
                          const SizedBox(height: 16),
                          if (_careDetails!['status']?.toString().toLowerCase() == 'completed')
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.green[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.green),
                              ),
                              child: const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.check_circle, color: Colors.green),
                                  SizedBox(width: 8),
                                  Text(
                                    'Garde terminée avec succès',
                                    style: TextStyle(
                                      color: Colors.green,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],

                        const SizedBox(height: 24),

                        // Localisation Section - En premier et bien visible
                        const Text(
                          'Localisation',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        _isEditMode && _isCurrentUserOwner()
                            ? TextField(
                                controller: _locationController,
                                style: const TextStyle(fontSize: 16),
                                decoration: const InputDecoration(
                                  hintText: 'Où se trouve la plante ?',
                                  border: OutlineInputBorder(),
                                  contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                                ),
                              )
                            : Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: Colors.blue[50],
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: Colors.blue[200]!),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.location_on, color: Colors.blue, size: 24),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Text(
                                        _careDetails?['localisation'] ?? 'Localisation non spécifiée',
                                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                        const SizedBox(height: 24),

                        // Plant Image Section
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Image de la Plante',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                            if (_isEditMode && _isCurrentUserOwner())
                              TextButton.icon(
                                onPressed: _selectPlantImage,
                                icon: const Icon(Icons.photo_camera, size: 16),
                                label: const Text('Changer', style: TextStyle(fontSize: 12)),
                              ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Container(
                          width: double.infinity,
                          height: 200,
                          decoration: BoxDecoration(
                            color: Colors.grey[200],
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: _newPlantImage != null
                              ? ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: Image.network(
                                    _newPlantImage!.path,
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) {
                                      return Container(
                                        color: Colors.blue[50],
                                        child: const Center(
                                          child: Column(
                                            mainAxisAlignment: MainAxisAlignment.center,
                                            children: [
                                              Icon(Icons.photo, color: Colors.blue, size: 40),
                                              Text('Nouvelle image sélectionnée', 
                                                style: TextStyle(color: Colors.blue)),
                                            ],
                                          ),
                                        ),
                                      );
                                    },
                                  ),
                                )
                              : _careDetails?['plant']?['photo'] != null
                                  ? ClipRRect(
                                      borderRadius: BorderRadius.circular(8),
                                      child: Image.network(
                                        _careDetails?['plant']?['photo'] ?? '',
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) {
                                          return const Center(
                                            child: Icon(Icons.error_outline, size: 40, color: Colors.grey),
                                          );
                                        },
                                      ),
                                    )
                                  : const Center(
                                      child: Icon(Icons.image_not_supported, size: 40, color: Colors.grey),
                                    ),
                        ),

                        const SizedBox(height: 16),
                        _isEditMode && _isCurrentUserOwner()
                            ? TextField(
                                controller: _plantNameController,
                                style: const TextStyle(fontSize: 14),
                                decoration: const InputDecoration(
                                  labelText: 'Nom de la plante',
                                  border: OutlineInputBorder(),
                                  contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                ),
                              )
                            : Text(
                                _careDetails!['plant']['nom'],
                                style: const TextStyle(fontSize: 14),
                              ),
                        Text(
                          'Type de Plante: ${_careDetails!['plant']['espece'] ?? 'Non spécifié'}',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),

                        const SizedBox(height: 24),

                        // Instructions Section
                        const Text(
                          'Instructions du propriétaire',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                                    _isEditMode && _isCurrentUserOwner()
                                        ? TextField(
                                            controller: _instructionsController,
                                            maxLines: 3,
                                            decoration: const InputDecoration(
                                              labelText: 'Instructions d\'entretien',
                                              border: OutlineInputBorder(),
                                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                            ),
                                          )
                                        : Text(_careDetails?['care_instructions'] ?? 'Aucune instruction spécifique'),
                            ],
                          ),
                        ),

                        const SizedBox(height: 24),
                        
                        // Care Reports Section - Visible pour tous les utilisateurs
                        if (_careDetails != null && _careDetails!['id'] != null) ...[
                          const Text(
                            'Rapports de séances d\'entretien',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          _isLoadingReports
                              ? const Center(child: CircularProgressIndicator())
                              : _careReports.isEmpty
                                  ? Container(
                                      padding: const EdgeInsets.all(16),
                                      decoration: BoxDecoration(
                                        color: Colors.grey[100],
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: const Row(
                                        children: [
                                          Icon(Icons.info_outline, color: Colors.grey),
                                          SizedBox(width: 12),
                                          Expanded(
                                            child: Text(
                                              'Aucun rapport de séance pour cette garde.',
                                              style: TextStyle(color: Colors.grey),
                                            ),
                                          ),
                                        ],
                                      ),
                                    )
                                  : Column(
                                      children: _careReports.map((report) => _buildCareReportCard(report)).toList(),
                                    ),
                          const SizedBox(height: 16),
                        ],

                        // Botanist Advice Section
                        const Text(
                          'Conseils de botanistes',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        _isLoadingAdvices
                            ? const Center(child: CircularProgressIndicator())
                            : _plantAdvices.isEmpty
                                ? Container(
                                    padding: const EdgeInsets.all(16),
                                    decoration: BoxDecoration(
                                      color: Colors.grey[100],
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: const Row(
                                      children: [
                                        Icon(Icons.info_outline, color: Colors.grey),
                                        SizedBox(width: 12),
                                        Expanded(
                                          child: Text(
                                            'Aucun conseil de botaniste pour cette plante.',
                                            style: TextStyle(color: Colors.grey),
                                          ),
                                        ),
                                      ],
                                    ),
                                  )
                                : Column(
                                    children: _plantAdvices.map((advice) => _buildAdviceCard(advice)).toList(),
                                  ),
                        const SizedBox(height: 16),
                      ],
                    ),
                  ),
                ),
      bottomNavigationBar: _careDetails != null ? _buildBottomNavigationBar() : null,
    );
  }

  Widget? _buildBottomNavigationBar() {
    if (_careDetails == null) return null;

    // Propriétaire qui peut terminer la garde
    if (_careDetails!['owner_id'] == _currentUserId &&
        (_careDetails!['status']?.toString().toLowerCase() == 'accepted' || 
         _careDetails!['status']?.toString().toLowerCase() == 'in_progress')) {
      return Padding(
        padding: const EdgeInsets.all(16.0),
        child: ElevatedButton(
          onPressed: _completeCare,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            padding: const EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text(
            'Terminer la garde',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      );
    }

    // Gardien qui peut faire un rapport (garde acceptée et en cours)
    if (_careDetails!['caretaker_id'] == _currentUserId &&
        (_careDetails!['status']?.toString().toLowerCase() == 'accepted' || 
         _careDetails!['status']?.toString().toLowerCase() == 'in_progress') &&
        _isInCarePeriod()) {
      
      final bool careHasStarted = _hasCareStarted();
      
      return Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (!careHasStarted)
              Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: Text(
                  'La garde n\'a pas encore commencé',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.orange[700],
                    fontSize: 14,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ElevatedButton(
              onPressed: careHasStarted ? () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => RapportDeGarde(plantCareId: widget.careId),
                  ),
                );
              } : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: careHasStarted ? Colors.green : Colors.grey,
                padding: const EdgeInsets.symmetric(vertical: 15),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                'Faire un rapport',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      );
    }

    // Gardien qui peut prendre la garde
    if (_careDetails!['status']?.toString().toLowerCase() == 'pending' && 
        _careDetails!['caretaker_id'] != _currentUserId) {
      return Padding(
        padding: const EdgeInsets.all(16.0),
        child: ElevatedButton(
          onPressed: _acceptCare,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            padding: const EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text(
            'Prendre la garde',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      );
    }

    return null;
  }
}