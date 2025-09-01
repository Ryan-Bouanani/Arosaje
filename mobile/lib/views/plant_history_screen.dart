import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:mobile/views/plant_care_details_screen.dart';
import 'package:mobile/services/plant_care_service.dart';
import 'package:mobile/services/storage_service.dart';

class PlantHistoryScreen extends StatefulWidget {
  const PlantHistoryScreen({super.key});

  @override
  _PlantHistoryScreenState createState() => _PlantHistoryScreenState();
}

class _PlantHistoryScreenState extends State<PlantHistoryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = "";
  
  late final PlantCareService _plantCareService;
  late final StorageService _storageService;
  bool _isInitialized = false;
  bool isLoading = true;
  String? error;

  List<Map<String, dynamic>> plantsConfiees = [];
  List<Map<String, dynamic>> plantsGardees = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      _storageService = await StorageService.init();
      _plantCareService = await PlantCareService.init();
      setState(() {
        _isInitialized = true;
      });
      await _loadHistory();
    } catch (e) {
      setState(() {
        error = 'Erreur d\'initialisation: ${e.toString()}';
        isLoading = false;
      });
    }
  }

  Future<void> _loadHistory() async {
    if (!_isInitialized) return;
    
    try {
      setState(() {
        isLoading = true;
        error = null;
      });

      // Charger l'historique des plantes confiées (je suis propriétaire)
      final completedOwned = await _plantCareService.getCompletedOwnedPlants();
      
      // Charger l'historique des plantes gardées (je suis gardien)
      final completedCaretaking = await _plantCareService.getCompletedCaretakingPlants();

      if (mounted) {
        setState(() {
          plantsConfiees = completedOwned;
          plantsGardees = completedCaretaking;
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString();
          isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Historique"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadHistory,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.green,
          labelColor: Colors.green,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(text: "Plantes Confiées"),
            Tab(text: "Plantes Gardées"),
          ],
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              controller: _searchController,
              onChanged: (value) {
                setState(() {
                  _searchQuery = value.toLowerCase();
                });
              },
              decoration: InputDecoration(
                hintText: "Rechercher...",
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildPlantConfieesTab(),
                _buildPlantGardeesTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlantConfieesTab() {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (error != null) {
      return Center(child: Text('Erreur: $error'));
    }

    final filteredCares = plantsConfiees
        .where((care) => 
          care['plant'] != null && 
          care['plant']['nom'] != null && 
          care['plant']['nom'].toLowerCase().contains(_searchQuery))
        .toList();

    if (filteredCares.isEmpty) {
      return const Center(child: Text('Aucune garde terminée'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredCares.length,
      itemBuilder: (context, index) {
        final care = filteredCares[index];
        final plant = care['plant'];
        final caretaker = care['caretaker'];
        final endDate = DateTime.parse(care['end_date']);
        
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 5),
          child: ListTile(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => PlantCareDetailsScreen(
                    isCurrentPlant: false,
                    careId: care['id'],
                  ),
                ),
              );
            },
            leading: CircleAvatar(
              backgroundColor: Colors.grey[200],
              child: plant['photo'] != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(50),
                      child: Image.network(
                        plant['photo'],
                        width: 40,
                        height: 40,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Icon(Icons.local_florist, color: Colors.green[700]);
                        },
                      ),
                    )
                  : Icon(Icons.local_florist, color: Colors.green[700]),
            ),
            title: Text(plant['nom'] ?? 'Plante'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Espèce: ${plant['espece'] ?? 'Non spécifiée'}'),
                if (caretaker != null)
                  Text('Gardé par ${caretaker['prenom'] ?? ''} ${caretaker['nom'] ?? ''}'),
                Text('Terminé le ${DateFormat('dd/MM/yyyy').format(endDate)}'),
              ],
            ),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.green,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'Terminé',
                style: TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildPlantGardeesTab() {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (error != null) {
      return Center(child: Text('Erreur: $error'));
    }

    final filteredCares = plantsGardees
        .where((care) => 
          care['plant'] != null && 
          care['plant']['nom'] != null && 
          care['plant']['nom'].toLowerCase().contains(_searchQuery))
        .toList();

    if (filteredCares.isEmpty) {
      return const Center(child: Text('Aucune garde terminée'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredCares.length,
      itemBuilder: (context, index) {
        final care = filteredCares[index];
        final plant = care['plant'];
        final owner = care['owner'];
        final endDate = DateTime.parse(care['end_date']);
        
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 5),
          child: ListTile(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => PlantCareDetailsScreen(
                    isCurrentPlant: false,
                    careId: care['id'],
                  ),
                ),
              );
            },
            leading: CircleAvatar(
              backgroundColor: Colors.grey[200],
              child: plant['photo'] != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(50),
                      child: Image.network(
                        plant['photo'],
                        width: 40,
                        height: 40,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Icon(Icons.local_florist, color: Colors.green[700]);
                        },
                      ),
                    )
                  : Icon(Icons.local_florist, color: Colors.green[700]),
            ),
            title: Text(plant['nom'] ?? 'Plante'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Espèce: ${plant['espece'] ?? 'Non spécifiée'}'),
                if (owner != null)
                  Text('Propriétaire: ${owner['prenom'] ?? ''} ${owner['nom'] ?? ''}'),
                Text('Terminé le ${DateFormat('dd/MM/yyyy').format(endDate)}'),
              ],
            ),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.green,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'Terminé',
                style: TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
          ),
        );
      },
    );
  }
}