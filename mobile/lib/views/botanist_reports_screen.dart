import 'package:flutter/material.dart';
import 'package:mobile/services/care_report_service.dart';
import 'package:mobile/widgets/image_zoom_dialog.dart';
import 'base_page_botaniste.dart';

class BotanistReportsScreen extends StatefulWidget {
  const BotanistReportsScreen({super.key});

  @override
  State<BotanistReportsScreen> createState() => _BotanistReportsScreenState();
}

class _BotanistReportsScreenState extends State<BotanistReportsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late final CareReportService _careReportService;
  
  List<Map<String, dynamic>> _allReports = [];
  List<Map<String, dynamic>> _myReviewedReports = [];
  
  bool _isLoadingAll = true;
  bool _isLoadingMy = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _initializeServices();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _initializeServices() async {
    try {
      _careReportService = await CareReportService.init();
      await _loadData();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoadingAll = false;
        _isLoadingMy = false;
      });
    }
  }

  Future<void> _loadData() async {
    try {
      await Future.wait([
        _loadAllReports(),
        _loadMyReviewedReports(),
      ]);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadAllReports() async {
    try {
      final reports = await _careReportService.getCareReportsForBotanist();
      setState(() {
        _allReports = reports;
        _isLoadingAll = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingAll = false;
      });
    }
  }

  Future<void> _loadMyReviewedReports() async {
    try {
      final reports = await _careReportService.getMyAdvisedReports();
      setState(() {
        _myReviewedReports = reports;
        _isLoadingMy = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingMy = false;
      });
    }
  }

  Color _getHealthColor(String? healthStatus) {
    switch (healthStatus?.toLowerCase()) {
      case 'bon':
        return Colors.green;
      case 'moyen':
        return Colors.orange;
      case 'bas':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Widget _buildReportCard(Map<String, dynamic> report, {bool isInAdviceTab = false}) {
    final healthStatus = report['health_level'] ?? 'Inconnu';
    final healthColor = _getHealthColor(healthStatus);
    final plantName = report['plant_care']?['plant']?['nom'] ?? 'Plante inconnue';
    final caretakerName = report['caretaker']?['prenom'] ?? 'Gardien inconnu';
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // En-tête avec statut
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    plantName,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: healthColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: healthColor),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        healthStatus.toLowerCase() == 'bon' 
                          ? Icons.check_circle
                          : healthStatus.toLowerCase() == 'moyen'
                            ? Icons.warning
                            : healthStatus.toLowerCase() == 'bas'
                              ? Icons.error
                              : Icons.help,
                        color: healthColor,
                        size: 16,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        healthStatus,
                        style: TextStyle(
                          color: healthColor,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 8),
            
            // Informations contextuelles
            Text('Gardien: $caretakerName'),
            Text(
              'Date: ${DateTime.parse(report['created_at']).day}/${DateTime.parse(report['created_at']).month}/${DateTime.parse(report['created_at']).year}',
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
            
            const SizedBox(height: 8),
            
            // Description
            if (report['description'] != null)
              Text(report['description']),
            
            const SizedBox(height: 12),
            
            // Photo
            if (report['photo_url'] != null)
              GestureDetector(
                onTap: () => ImageZoomDialog.show(context, report['photo_url']),
                child: Container(
                  width: 80,
                  height: 80,
                  margin: const EdgeInsets.only(bottom: 8),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.grey[300]!),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(7),
                    child: Image.network(
                      report['photo_url'],
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          color: Colors.grey[200],
                          child: const Icon(Icons.broken_image, color: Colors.grey),
                        );
                      },
                      loadingBuilder: (context, child, loadingProgress) {
                        if (loadingProgress == null) return child;
                        return Container(
                          color: Colors.grey[200],
                          child: const Center(
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        );
                      },
                    ),
                  ),
                ),
              ),
            
            const SizedBox(height: 12),
            
            // Actions
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: () => _showReportDetails(report),
                  icon: const Icon(Icons.visibility, size: 16),
                  label: const Text('Voir détails'),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () => _showAddAdviceDialog(report, isUpdate: isInAdviceTab),
                  icon: Icon(isInAdviceTab ? Icons.edit : Icons.add_comment, size: 16),
                  label: Text(isInAdviceTab ? 'Modifier l\'avis' : 'Ajouter avis'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: isInAdviceTab ? Colors.orange : Colors.green,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showReportDetails(Map<String, dynamic> report) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Détails du rapport'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Plante: ${report['plant_care']?['plant']?['nom'] ?? 'Inconnue'}'),
              Text('Gardien: ${report['caretaker']?['prenom'] ?? 'Inconnu'}'),
              Text('État santé: ${report['health_level'] ?? 'Inconnu'}'),
              Text('Hydratation: ${report['hydration_level'] ?? 'Inconnu'}'),
              Text('Vitalité: ${report['vitality_level'] ?? 'Inconnu'}'),
              const SizedBox(height: 8),
              if (report['description'] != null) ...[
                const Text('Description:', style: TextStyle(fontWeight: FontWeight.bold)),
                Text(report['description']),
              ],
              // TODO: Afficher les avis botanistes existants
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Fermer'),
          ),
        ],
      ),
    );
  }

  void _showAddAdviceDialog(Map<String, dynamic> report, {bool isUpdate = false}) {
    final TextEditingController adviceController = TextEditingController();
    
    // Si c'est une mise à jour, pré-remplir avec l'avis existant (le plus récent)
    if (isUpdate && report['botanist_advices'] != null && (report['botanist_advices'] as List).isNotEmpty) {
      // Prendre le dernier avis (le plus récent)
      final latestAdvice = (report['botanist_advices'] as List).last;
      adviceController.text = latestAdvice['advice_text'] ?? '';
    }
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${isUpdate ? 'Modifier l\'avis' : 'Avis'} pour ${report['plant_care']?['plant']?['nom'] ?? 'la plante'}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('État constaté: ${report['health_level'] ?? 'Inconnu'}'),
            const SizedBox(height: 16),
            TextField(
              controller: adviceController,
              maxLines: 5,
              decoration: InputDecoration(
                labelText: isUpdate ? 'Nouvelle version de votre avis' : 'Votre avis expert',
                hintText: 'Diagnostic, recommandations, observations...',
                border: const OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Annuler'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (adviceController.text.trim().isNotEmpty) {
                try {
                  if (isUpdate) {
                    await _updateAdviceToReport(report, adviceController.text.trim());
                  } else {
                    await _addAdviceToReport(report['id'], adviceController.text.trim());
                  }
                  if (mounted) {
                    Navigator.pop(context);
                  }
                } catch (e) {
                  // Error handling is done in the methods
                }
              }
            },
            child: Text(isUpdate ? 'Modifier l\'avis' : 'Ajouter avis'),
          ),
        ],
      ),
    );
  }

  Future<void> _addAdviceToReport(int reportId, String adviceText) async {
    try {
      final response = await _careReportService.addAdviceToReport(reportId, adviceText);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Avis ajouté avec succès !'),
            backgroundColor: Colors.green,
          ),
        );
      }
      
      if (mounted) {
        setState(() {
          _isLoadingAll = true;
          _isLoadingMy = true;
        });
        
        await _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _updateAdviceToReport(Map<String, dynamic> report, String adviceText) async {
    try {
      // Récupérer l'ID de mon avis pour ce rapport
      final advices = report['botanist_advices'] as List<dynamic>?;
      if (advices == null || advices.isEmpty) {
        throw Exception('Aucun avis trouvé à modifier');
      }
      
      // Prendre le dernier avis (le plus récent) - normalement c'est le mien
      final latestAdvice = advices.last;
      final adviceId = latestAdvice['id'];
      
      final response = await _careReportService.updateAdviceToReport(adviceId, adviceText);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Avis modifié avec succès !'),
            backgroundColor: Colors.green,
          ),
        );
      }
      
      if (mounted) {
        setState(() {
          _isLoadingAll = true;
          _isLoadingMy = true;
        });
        
        await _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildAllReportsTab() {
    if (_isLoadingAll) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_allReports.isEmpty) {
      return const Center(
        child: Text('Aucun rapport de garde disponible.'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _allReports.length,
      itemBuilder: (context, index) => _buildReportCard(_allReports[index], isInAdviceTab: false),
    );
  }

  Widget _buildMyReviewsTab() {
    if (_isLoadingMy) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_myReviewedReports.isEmpty) {
      return const Center(
        child: Text('Vous n\'avez encore donné d\'avis sur aucun rapport.'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _myReviewedReports.length,
      itemBuilder: (context, index) => _buildReportCard(_myReviewedReports[index], isInAdviceTab: true),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BasePageBotaniste(
      currentIndex: 2,
      body: Scaffold(
        appBar: AppBar(
          title: const Text('Rapports de Garde'),
          backgroundColor: Colors.green,
          foregroundColor: Colors.white,
          automaticallyImplyLeading: false,
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: const [
              Tab(text: 'À examiner'),
              Tab(text: 'Mes avis'),
            ],
          ),
        ),
        body:
        _error != null
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(_error!, style: const TextStyle(color: Colors.red)),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loadData,
                      child: const Text('Réessayer'),
                    ),
                  ],
                ),
              )
            : TabBarView(
                controller: _tabController,
                children: [
                  _buildAllReportsTab(),
                  _buildMyReviewsTab(),
                ],
              ),
      ),
    );
  }
}