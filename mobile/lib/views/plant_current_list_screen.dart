import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:mobile/views/plant_care_details_screen.dart';
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
  late final PlantCareService _plantCareService;
  late final StorageService _storageService;
  bool _isInitialized = false;

  List<Map<String, dynamic>> mesGardes = []; // Plantes confiées (je suis propriétaire)
  List<Map<String, dynamic>> mesCaretaking = []; // Mes gardes (je suis gardien)
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

      // Charger mes plantes confiées (je suis propriétaire)
      final myOwnedPlantCares = await _plantCareService.getMyPlantCares();
      
      // Charger les plantes que je garde (je suis gardien)
      final myCaretakingPlants = await _plantCareService.getMyCaretakingPlants();

      if (mounted) {
        setState(() {
          mesGardes = myOwnedPlantCares; // Plantes confiées (propriétaire)
          mesCaretaking = myCaretakingPlants; // Mes gardes (gardien)
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
        title: const Text("Mes Plantes Confiées"),
        automaticallyImplyLeading: false,
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
            Tab(text: "Mes Plantes Confiées"),
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
    // Trier les gardes par date de création (plus récentes en premier)
    final sortedCares = List<Map<String, dynamic>>.from(mesGardes)
      ..sort((a, b) {
        final aDate = DateTime.parse(a['created_at'] ?? a['start_date']);
        final bDate = DateTime.parse(b['created_at'] ?? b['start_date']);
        return bDate.compareTo(aDate); // Plus récent d'abord
      });

    final filteredCares = sortedCares
        .where((care) => 
          care['plant'] != null && 
          care['plant']['nom'] != null && 
          care['plant']['nom'].toLowerCase().contains(_searchQuery))
        .toList();

    if (filteredCares.isEmpty) {
      return const Center(child: Text('Aucune plante confiée'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredCares.length,
      itemBuilder: (context, index) {
        final care = filteredCares[index];
        final plant = care['plant'];
        final startDate = DateTime.parse(care['start_date']);
        final endDate = DateTime.parse(care['end_date']);
        final owner = care['owner'];

        return Column(
          children: [
            ListTile(
              leading: CircleAvatar(
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
              title: Text(plant['nom'] ?? 'Plante'),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Propriétaire: ${owner['prenom']} ${owner['nom']}'),
                  Text('Du ${DateFormat('dd/MM/yy').format(startDate)} au ${DateFormat('dd/MM/yy').format(endDate)}'),
                  if (care['localisation'] != null)
                    Text('Lieu: ${care['localisation']}', 
                      style: const TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
              trailing: const Icon(Icons.chevron_right),
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
            ),
            const Divider(),
          ],
        );
      },
    );
  }

  Widget _buildMyCaretakingList() {
    final filteredCares = mesCaretaking
        .where((care) => 
          care['plant'] != null && 
          care['plant']['nom'] != null && 
          care['plant']['nom'].toLowerCase().contains(_searchQuery))
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
                  if (mesCaretaking.any((care) => 
                    care['plant'] != null &&
                    care['plant']['id'] == plant['id'] && 
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
                plant['nom'] ?? 'Plante sans nom',
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
