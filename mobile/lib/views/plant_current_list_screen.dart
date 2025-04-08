import 'package:flutter/material.dart';
import 'package:mobile/views/plant_care_details_screen.dart';
import 'package:mobile/models/plant.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/services/storage_service.dart';
import 'package:mobile/services/plant_care_service.dart';

class PlantCurrentListScreen extends StatefulWidget {
  const PlantCurrentListScreen({super.key});

  @override
  _PlantCurrentListScreenState createState() => _PlantCurrentListScreenState();
}

class _PlantCurrentListScreenState extends State<PlantCurrentListScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = "";
  late final PlantService _plantService;
  late final PlantCareService _plantCareService;
  late final StorageService _storageService;
  bool _isInitialized = false;

  List<Plant> mesPlantes = [];
  List<Map<String, dynamic>> mesGardes = [];
  bool isLoading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      _storageService = await StorageService.init();
      _plantService = await PlantService.init();
      _plantCareService = await PlantCareService.init();
      setState(() {
        _isInitialized = true;
      });
      await _loadPlants();
    } catch (e) {
      setState(() {
        error = 'Erreur d\'initialisation: ${e.toString()}';
        isLoading = false;
      });
    }
  }

  Future<void> _loadPlants() async {
    if (!_isInitialized) return;
    
    try {
      setState(() {
        isLoading = true;
        error = null;
      });

      // Charger mes plantes
      final myPlants = await _plantService.getMyPlants();
      
      // Charger les plantes que je garde
      final myCaretakingPlants = await _plantCareService.getMyPlantCares();

      if (mounted) {
        setState(() {
          mesPlantes = myPlants;
          mesGardes = myCaretakingPlants;
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
        title: const Text("Mes plantes"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadPlants,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.green,
          labelColor: Colors.green,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(text: "Mes plantes"),
            Tab(text: "Mes gardes"),
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
                hintText: "Recherche",
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(30),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[200],
              ),
            ),
          ),
          Expanded(
            child: isLoading 
              ? const Center(child: CircularProgressIndicator())
              : error != null
                ? Center(child: Text(error!, style: const TextStyle(color: Colors.red)))
                : TabBarView(
                    controller: _tabController,
                    children: [
                      _buildMyPlantsList(),
                      _buildMyCaretakingList(),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildMyPlantsList() {
    final filteredPlants = mesPlantes
        .where((plant) => plant.nom.toLowerCase().contains(_searchQuery))
        .toList();

    if (filteredPlants.isEmpty) {
      return const Center(child: Text('Aucune plante trouvée'));
    }

    Widget _buildCareStatusBadge(String status) {
      IconData icon;
      Color color;
      String text;

      switch (status) {
        case 'PENDING':
          icon = Icons.hourglass_empty;
          color = Colors.orange;
          text = 'En attente';
          break;
        case 'ACCEPTED':
          icon = Icons.check_circle;
          color = Colors.blue;
          text = 'Acceptée';
          break;
        case 'REFUSED':
          icon = Icons.cancel;
          color = Colors.red;
          text = 'Refusée';
          break;
        case 'IN_PROGRESS':
          icon = Icons.volunteer_activism;
          color = Colors.green;
          text = 'En garde';
          break;
        case 'COMPLETED':
          icon = Icons.task_alt;
          color = Colors.purple;
          text = 'Terminée';
          break;
        case 'CANCELLED':
          icon = Icons.block;
          color = Colors.grey;
          text = 'Annulée';
          break;
        default:
          return const SizedBox.shrink();
      }

      return Container(
        padding: const EdgeInsets.all(4),
        decoration: BoxDecoration(
          color: color.withOpacity(0.2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16,
              color: color,
            ),
            const SizedBox(width: 4),
            Text(
              text,
              style: TextStyle(
                fontSize: 12,
                color: color,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredPlants.length,
      itemBuilder: (context, index) {
        final plant = filteredPlants[index];
        // Trouver si la plante a une garde et son statut
        final care = mesGardes.firstWhere(
          (care) => care['plant']['id'] == plant.id,
          orElse: () => <String, dynamic>{},
        );
        final String? careStatus = care.isNotEmpty ? care['status'] as String : null;

        return Column(
          children: [
            ListTile(
              leading: Stack(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.grey[200],
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(50),
                      child: plant.photo != null
                        ? Image.network(
                            plant.photo!,
                            width: 40,
                            height: 40,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Icon(
                                Icons.local_florist,
                                color: Colors.green[700],
                              );
                            },
                          )
                        : Icon(
                            Icons.local_florist,
                            color: Colors.green[700],
                          ),
                    ),
                  ),
                  if (careStatus != null)
                    Positioned(
                      right: -5,
                      bottom: -5,
                      child: _buildCareStatusBadge(careStatus),
                    ),
                ],
              ),
              title: Text(
                plant.nom,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text(plant.espece ?? 'Espèce non spécifiée'),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => PlantCareDetailsScreen(
                      isCurrentPlant: true,
                      plantId: plant.id,
                    ),
                  ),
                );
              },
            ),
            const Divider(),
          ],
        );
      },
    );
  }

  Widget _buildMyCaretakingList() {
    final filteredCares = mesGardes
        .where((care) => care['plant']['nom'].toLowerCase().contains(_searchQuery))
        .toList();

    if (filteredCares.isEmpty) {
      return const Center(child: Text('Aucune garde en cours'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredCares.length,
      itemBuilder: (context, index) {
        final care = filteredCares[index];
        final plant = care['plant'];
        final startDate = DateTime.parse(care['start_date']);
        final endDate = DateTime.parse(care['end_date']);

        return Column(
          children: [
            ListTile(
              leading: Stack(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.grey[200],
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(50),
                      child: plant['photo'] != null
                        ? Image.network(
                            plant['photo'],
                            width: 40,
                            height: 40,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Icon(
                                Icons.local_florist,
                                color: Colors.green[700],
                              );
                            },
                          )
                        : Icon(
                            Icons.local_florist,
                            color: Colors.green[700],
                          ),
                    ),
                  ),
                  if (mesGardes.any((care) => 
                    care['plant']['id'] == plant.id && 
                    care['status'] == 'in_progress'
                  ))
                    Positioned(
                      right: -5,
                      bottom: -5,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.green[700],
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: Colors.white,
                            width: 2,
                          ),
                        ),
                        child: const Icon(
                          Icons.volunteer_activism,
                          size: 12,
                          color: Colors.white,
                        ),
                      ),
                    ),
                ],
              ),
              title: Text(
                plant['nom'],
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(plant['espece'] ?? 'Espèce non spécifiée'),
                  Text(
                    'Du ${startDate.day}/${startDate.month}/${startDate.year} au ${endDate.day}/${endDate.month}/${endDate.year}',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                ],
              ),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => PlantCareDetailsScreen(
                      isCurrentPlant: true,
                      careId: care['id'],
                    ),
                  ),
                );
              },
            ),
            const Divider(),
          ],
        );
      },
    );
  }
}
