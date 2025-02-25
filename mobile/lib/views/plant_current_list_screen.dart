import 'package:flutter/material.dart';
import 'package:mobile/views/plant_care_details_screen.dart';
import 'package:mobile/models/plant.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/services/storage_service.dart';

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
  late final StorageService _storageService;
  bool _isInitialized = false;

  List<Plant> plantsConfieesEnCours = [];
  List<Plant> plantsGardeesEnCours = [];
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

      final userId = await _storageService.getUserId();
      if (userId == null) throw Exception('Utilisateur non connecté');

      // Charger les plantes confiées (mes plantes)
      final myPlants = await _plantService.getMyPlants();
      
      // Charger les plantes gardées (plantes dont je suis le gardien)
      final plantsGardees = await _plantService.getPlantsByOwner(userId);

      if (mounted) {
        setState(() {
          plantsConfieesEnCours = myPlants;
          plantsGardeesEnCours = plantsGardees;
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
        title: const Text("Plantes en cours"),
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
                      _buildPlantList(plantsConfieesEnCours),
                      _buildPlantList(plantsGardeesEnCours),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlantList(List<Plant> plants) {
    final filteredPlants = plants
        .where((plant) => plant.nom.toLowerCase().contains(_searchQuery))
        .toList();

    if (filteredPlants.isEmpty) {
      return const Center(child: Text('Aucune plante trouvée'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredPlants.length,
      itemBuilder: (context, index) {
        final plant = filteredPlants[index];
        return Column(
          children: [
            ListTile(
              leading: CircleAvatar(
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
}
