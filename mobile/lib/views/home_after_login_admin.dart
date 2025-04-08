import 'package:flutter/material.dart';
import 'base_page_botaniste.dart';
import 'plant_detail_botaniste.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/models/plant.dart';
import 'package:mobile/services/plant_care_service.dart';

class HomeAfterLoginAdmin extends StatefulWidget {
  const HomeAfterLoginAdmin({super.key});

  @override
  State<HomeAfterLoginAdmin> createState() => _HomeAfterLoginAdminState();
}

class _HomeAfterLoginAdminState extends State<HomeAfterLoginAdmin> {
  final TextEditingController _searchController = TextEditingController();
  late final PlantService _plantService;
  late final PlantCareService _plantCareService;
  bool _isInitialized = false;
  bool _isLoading = true;
  String? _error;
  List<Plant> _allPlants = [];
  String _searchQuery = "";

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      _plantService = await PlantService.init();
      _plantCareService = await PlantCareService.init();
      setState(() {
        _isInitialized = true;
      });
      await _loadPlants();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadPlants() async {
    if (!_isInitialized) return;
    
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final plants = await _plantService.getAllPlants();
      
      if (mounted) {
        setState(() {
          _allPlants = plants;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Widget _buildPlantCard(Plant plant) {
    return GestureDetector(
      onTap: () {
        _showPlantDetails(plant);
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.2),
              spreadRadius: 1,
              blurRadius: 5,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              flex: 2,
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(12),
                    topRight: Radius.circular(12),
                  ),
                ),
                child: plant.photo != null
                  ? ClipRRect(
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(12),
                        topRight: Radius.circular(12),
                      ),
                      child: Image.network(
                        plant.photo!,
                        fit: BoxFit.cover,
                        width: double.infinity,
                        errorBuilder: (context, error, stackTrace) {
                          return Icon(
                            Icons.local_florist,
                            size: 40,
                            color: Colors.green[700],
                          );
                        },
                      ),
                    )
                  : Center(
                      child: Icon(
                        Icons.local_florist,
                        size: 40,
                        color: Colors.green[700],
                      ),
                    ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      plant.nom,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (plant.espece != null)
                      Text(
                        plant.espece!,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showPlantDetails(Plant plant) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PlantDetailBotaniste(
          plantId: plant.id,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final filteredPlants = _allPlants
        .where((plant) => plant.nom.toLowerCase().contains(_searchQuery.toLowerCase()))
        .toList();

    return BasePageBotaniste(
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Gestion des plantes',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Container(
                height: 200,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Center(
                  child: Text('Carte des plantes à proximité'),
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.2),
                      spreadRadius: 1,
                      blurRadius: 5,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Rechercher une plante...',
                    border: InputBorder.none,
                    icon: Icon(Icons.search, color: Colors.grey[600]),
                    suffixIcon: IconButton(
                      icon: Icon(Icons.filter_list, color: Colors.grey[600]),
                      onPressed: () {
                        // Logique de filtrage
                      },
                    ),
                  ),
                  onChanged: (value) {
                    setState(() {
                      _searchQuery = value;
                    });
                  },
                ),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Plantes enregistrées',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  TextButton(
                    onPressed: _loadPlants,
                    child: const Text(
                      'Actualiser',
                      style: TextStyle(color: Colors.green),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (_isLoading)
                const Center(child: CircularProgressIndicator())
              else if (_error != null)
                Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
              else if (filteredPlants.isEmpty)
                const Center(child: Text('Aucune plante trouvée'))
              else
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: 0.75,
                  ),
                  itemCount: filteredPlants.length,
                  itemBuilder: (context, index) => _buildPlantCard(filteredPlants[index]),
                ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      currentIndex: 0,
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
}
