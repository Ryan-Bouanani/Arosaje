import 'package:flutter/material.dart';
import 'package:mobile/services/plant_care_advice_service.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/models/plant_care_advice.dart';
import 'package:mobile/views/create_advice_screen.dart';
import 'package:mobile/views/validate_advice_screen.dart';

class BotanistAdviceScreen extends StatefulWidget {
  const BotanistAdviceScreen({super.key});

  @override
  State<BotanistAdviceScreen> createState() => _BotanistAdviceScreenState();
}

class _BotanistAdviceScreenState extends State<BotanistAdviceScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late final PlantCareAdviceService _plantCareAdviceService;
  late final ApiService _apiService;
  
  List<PlantCareWithAdvice> _myAdvices = [];
  List<PlantCareWithAdvice> _allPlantCares = [];
  List<PlantCareWithAdvice> _pendingRequests = [];
  
  bool _isLoadingAdvices = true;
  bool _isLoadingPlants = true;
  bool _isLoadingRequests = true;
  
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _initializeServices();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _initializeServices() async {
    try {
      _plantCareAdviceService = PlantCareAdviceService();
      _apiService = ApiService();
      await _loadData();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoadingAdvices = false;
        _isLoadingPlants = false;
        _isLoadingRequests = false;
      });
    }
  }

  Future<void> _loadData() async {
    await Future.wait([
      _loadMyAdvices(),
      _loadAllPlantCares(),
      _loadPendingRequests(),
    ]);
  }

  Future<void> _loadMyAdvices() async {
    try {
      final advices = await _plantCareAdviceService.getPlantCaresWithAdvice(myAdviceOnly: true);
      setState(() {
        _myAdvices = advices;
        _isLoadingAdvices = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingAdvices = false;
      });
    }
  }

  Future<void> _loadAllPlantCares() async {
    try {
      final plantCares = await _plantCareAdviceService.getPlantCaresToReview();
      setState(() {
        _allPlantCares = plantCares;
        _isLoadingPlants = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingPlants = false;
      });
    }
  }

  Future<void> _loadPendingRequests() async {
    try {
      final requests = await _plantCareAdviceService.getPlantCaresToReview();
      setState(() {
        _pendingRequests = requests;
        _isLoadingRequests = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingRequests = false;
      });
    }
  }

  Color _getPriorityColor(AdvicePriority priority) {
    switch (priority) {
      case AdvicePriority.low:
        return Colors.blue;
      case AdvicePriority.normal:
        return Colors.orange;
      case AdvicePriority.high:
        return Colors.red;
      case AdvicePriority.urgent:
        return Colors.purple;
    }
  }

  void _navigateToCreateAdvice(PlantCareWithAdvice plantCare) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CreateAdviceScreen(
          plantCare: plantCare,
          onAdviceCreated: () {
            _loadData(); // Refresh data after advice creation
          },
        ),
      ),
    );
  }

  void _navigateToValidateAdvice(PlantCareWithAdvice plantCare, PlantCareAdvice advice) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ValidateAdviceScreen(
          advice: advice,
          plantCare: plantCare,
          onValidated: () {
            _loadData(); // Refresh data after validation
          },
        ),
      ),
    );
  }


  Widget _buildMyAdvicesTab() {
    if (_isLoadingAdvices) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_myAdvices.isEmpty) {
      return const Center(
        child: Text('Vous n\'avez donné aucun conseil pour le moment.'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _myAdvices.length,
      itemBuilder: (context, index) {
        final plantCareWithAdvice = _myAdvices[index];
        final advice = plantCareWithAdvice.advice;
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        plantCareWithAdvice.plantName,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    if (advice != null)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: advice.validationStatus == ValidationStatus.validated ? Colors.green[50] : Colors.orange[50],
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(
                            color: advice.validationStatus == ValidationStatus.validated ? Colors.green : Colors.orange,
                          ),
                        ),
                        child: Text(
                          advice.validationStatus.displayName,
                          style: TextStyle(
                            color: advice.validationStatus == ValidationStatus.validated ? Colors.green : Colors.orange,
                            fontSize: 12,
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                if (advice != null) ...[
                  Text(advice.title, style: const TextStyle(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 4),
                  Text(advice.content),
                  const SizedBox(height: 8),
                ],
                if (plantCareWithAdvice.plantSpecies != null)
                  Text(
                    'Espèce: ${plantCareWithAdvice.plantSpecies}',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                Text(
                  'Propriétaire: ${plantCareWithAdvice.ownerName}',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPlantsTab() {
    if (_isLoadingPlants) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_allPlantCares.isEmpty) {
      return const Center(
        child: Text('Aucune garde à examiner.'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _allPlantCares.length,
      itemBuilder: (context, index) {
        final plantCare = _allPlantCares[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: const CircleAvatar(
              backgroundColor: Colors.green,
              child: Icon(Icons.local_florist, color: Colors.white),
            ),
            title: Text(plantCare.plantName),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (plantCare.plantSpecies != null)
                  Text('Espèce: ${plantCare.plantSpecies}'),
                Text('Propriétaire: ${plantCare.ownerName}'),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: _getPriorityColor(plantCare.priority).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    plantCare.priority.displayName,
                    style: TextStyle(
                      color: _getPriorityColor(plantCare.priority),
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            trailing: ElevatedButton.icon(
              onPressed: () => _navigateToCreateAdvice(plantCare),
              icon: const Icon(Icons.add_comment, size: 16),
              label: const Text('Conseil'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildPendingRequestsTab() {
    if (_isLoadingRequests) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_pendingRequests.isEmpty) {
      return const Center(
        child: Text('Aucune demande de conseil en attente.'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _pendingRequests.length,
      itemBuilder: (context, index) {
        final plantCareWithAdvice = _pendingRequests[index];
        final advice = plantCareWithAdvice.advice;
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        plantCareWithAdvice.plantName,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: _getPriorityColor(plantCareWithAdvice.priority).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        plantCareWithAdvice.priority.displayName,
                        style: TextStyle(
                          color: _getPriorityColor(plantCareWithAdvice.priority),
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                if (plantCareWithAdvice.plantSpecies != null)
                  Text('Espèce: ${plantCareWithAdvice.plantSpecies}'),
                Text('Propriétaire: ${plantCareWithAdvice.ownerName}'),
                if (advice != null) ...[
                  const SizedBox(height: 8),
                  Text('Titre: ${advice.title}'),
                  Text('Conseil: ${advice.content}'),
                ],
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    if (advice != null) ...[
                      TextButton(
                        onPressed: () => _navigateToValidateAdvice(plantCareWithAdvice, advice),
                        child: const Text('Évaluer'),
                      ),
                    ] else ...[
                      ElevatedButton(
                        onPressed: () => _navigateToCreateAdvice(plantCareWithAdvice),
                        child: const Text('Donner un conseil'),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Interface Botaniste'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: 'Mes Conseils'),
            Tab(text: 'Gardes à Examiner'),
            Tab(text: 'Demandes'),
          ],
        ),
      ),
      body: _error != null
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
                _buildMyAdvicesTab(),
                _buildPlantsTab(),
                _buildPendingRequestsTab(),
              ],
            ),
    );
  }
}