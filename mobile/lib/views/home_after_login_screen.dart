import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'base_page.dart';
import 'add_plant_screen.dart';
import 'plant_care_details_screen.dart';
import 'package:mobile/models/plant.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/services/plant_care_service.dart';
import 'package:geolocator/geolocator.dart';

class HomeAfterLogin extends StatefulWidget {
  const HomeAfterLogin({super.key});

  @override
  State<HomeAfterLogin> createState() => _HomeAfterLoginState();
}

class _HomeAfterLoginState extends State<HomeAfterLogin> {
  late final PlantCareService _plantCareService;
  List<Map<String, dynamic>> _pendingCares = [];
  bool _isLoading = true;
  String? _error;
  LatLng? _userLocation;

  // Données des plantes avec localisation
  final List<Map<String, dynamic>> _nearbyPlants = [
    {
      'id': 1,
      'nom': 'Monstera Deliciosa',
      'espece': 'Monstera',
      'photo': 'https://example.com/photos/monstera.jpg',
      'location': const LatLng(48.8566, 2.3522), // Paris
      'address': '12 Rue de Rivoli, 75001 Paris',
    },
    {
      'id': 2,
      'nom': 'Ficus Lyrata',
      'espece': 'Ficus',
      'photo': 'https://example.com/photos/ficus.jpg',
      'location': const LatLng(48.8606, 2.3376), // Louvre
      'address': '36 Quai des Orfèvres, 75001 Paris',
    },
    {
      'id': 3,
      'nom': 'Calathea Orbifolia',
      'espece': 'Calathea',
      'photo': 'https://example.com/photos/calathea.jpg',
      'location': const LatLng(48.8738, 2.2950), // Arc de Triomphe
      'address': '8 Avenue Montaigne, 75008 Paris',
    },
    {
      'id': 4,
      'nom': 'Pilea Peperomioides',
      'espece': 'Pilea',
      'photo': 'https://example.com/photos/pilea.jpg',
      'location': const LatLng(48.8649, 2.3800), // Bastille
      'address': '15 Rue de la Roquette, 75011 Paris',
    },
  ];

  // Point central de la carte (Paris)
  final LatLng _center = const LatLng(48.8566, 2.3522);

  String formatDateNumber(int number) {
    return number.toString().padLeft(2, '0');
  }

  @override
  void initState() {
    super.initState();
    _initializeService();
    _getUserLocation();
  }

  Future<void> _getUserLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) return;

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) return;
      }
      if (permission == LocationPermission.deniedForever) return;

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      setState(() {
        _userLocation = LatLng(position.latitude, position.longitude);
      });
    } catch (e) {
      print("Erreur localisation: $e");
    }
  }

  Future<void> _initializeService() async {
    try {
      _plantCareService = await PlantCareService.init();
      await _loadPendingCares();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadPendingCares() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final cares = await _plantCareService.getPendingPlantCares();

      if (mounted) {
        setState(() {
          _pendingCares = cares;
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

  // Widget pour afficher la carte
  Widget _buildMap() {
    return Container(
      height: 300,
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.3),
            spreadRadius: 1,
            blurRadius: 5,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: FlutterMap(
          options: MapOptions(
            initialCenter: _center, // Change 'center' to 'initialCenter'
            initialZoom: 13.0, // Change 'zoom' to 'initialZoom'
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.example.app',
            ),
            MarkerLayer(
              markers: [
                if (_userLocation != null)
                  Marker(
                    point: _userLocation!,
                    width: 40,
                    height: 40,
                    child: const Icon(
                      Icons.person_pin_circle,
                      color: Colors.blue,
                      size: 30,
                    ),
                  ),
                ..._nearbyPlants
                    .map(
                      (plant) => Marker(
                        point: plant['location'],
                        width: 40,
                        height: 40,
                        child: GestureDetector(
                          onTap: () {
                            _showPlantDetails(plant);
                          },
                          child: Container(
                            decoration: const BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.green,
                            ),
                            child: const Icon(
                              Icons.local_florist,
                              color: Colors.white,
                              size: 20,
                            ),
                          ),
                        ),
                      ),
                    )
                    .toList(),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // Afficher les détails d'une plante sur la carte
  void _showPlantDetails(Map<String, dynamic> plant) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child:
                        plant['photo'] != null
                            ? ClipRRect(
                              borderRadius: BorderRadius.circular(10),
                              child: Image.network(
                                plant['photo'],
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) {
                                  return Icon(
                                    Icons.local_florist,
                                    size: 30,
                                    color: Colors.green[700],
                                  );
                                },
                              ),
                            )
                            : Icon(
                              Icons.local_florist,
                              size: 30,
                              color: Colors.green[700],
                            ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          plant['nom'],
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                        Text(
                          plant['espece'],
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Icon(Icons.location_on, color: Colors.green[700], size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      plant['address'],
                      style: TextStyle(color: Colors.grey[800]),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    // Ici vous pourriez naviguer vers une page de détails de la plante
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                  ),
                  child: const Text('Voir les détails'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCareCard(BuildContext context, Map<String, dynamic> care) {
    final plant = care['plant'];
    final startDate = DateTime.parse(care['start_date']);
    final endDate = DateTime.parse(care['end_date']);

    return GestureDetector(
      onTap: () async {
        final result = await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => PlantCareDetailsScreen(
              isCurrentPlant: false,
              careId: care['id'],
            ),
          ),
        );
        if (result == true) {
          await _loadPendingCares();
        }
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withAlpha(3),
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
                child:
                    plant != null && plant['photo'] != null
                        ? ClipRRect(
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(12),
                            topRight: Radius.circular(12),
                          ),
                          child: Image.network(
                            plant['photo'],
                            fit: BoxFit.cover,
                            width: double.infinity,
                            errorBuilder: (context, error, stackTrace) {
                              print('Erreur de chargement de l\'image: $error');
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
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          plant != null ? plant['nom'] : 'Plante inconnue',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          plant != null
                              ? (plant['espece'] ?? 'Espèce non spécifiée')
                              : 'Espèce inconnue',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 12,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                    Text(
                      'Du ${formatDateNumber(startDate.day)}/${formatDateNumber(startDate.month)} au ${formatDateNumber(endDate.day)}/${formatDateNumber(endDate.month)}',
                      style: TextStyle(color: Colors.grey[600], fontSize: 12),
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

  // Widget pour afficher la liste des plantes à proximité
  Widget _buildNearbyPlantsList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Liste des plantes à proximité',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _nearbyPlants.length,
          itemBuilder: (context, index) {
            final plant = _nearbyPlants[index];
            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: ListTile(
                contentPadding: const EdgeInsets.all(12),
                leading: Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child:
                      plant['photo'] != null
                          ? ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(
                              plant['photo'],
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return Icon(
                                  Icons.local_florist,
                                  size: 25,
                                  color: Colors.green[700],
                                );
                              },
                            ),
                          )
                          : Icon(
                            Icons.local_florist,
                            size: 25,
                            color: Colors.green[700],
                          ),
                ),
                title: Text(
                  plant['nom'],
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(plant['espece']),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.location_on,
                          size: 14,
                          color: Colors.green[700],
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            plant['address'],
                            style: const TextStyle(fontSize: 12),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                onTap: () => _showPlantDetails(plant),
              ),
            );
          },
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return BasePage(
      body: RefreshIndicator(
        onRefresh: _loadPendingCares,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Plantes à proximité',
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                // Carte OpenStreetMap
                _buildMap(),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Plantes à garder proche de vous',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (_isLoading)
                      const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                if (_error != null)
                  Center(
                    child: Text(
                      _error!,
                      style: const TextStyle(color: Colors.red),
                    ),
                  )
                else if (_pendingCares.isEmpty && !_isLoading)
                  const Center(
                    child: Text(
                      'Aucune garde en attente disponible pour le moment',
                    ),
                  )
                else
                  ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _pendingCares.length,
                    itemBuilder: (context, index) {
                      final care = _pendingCares[index];
                      final plant = care['plant'];
                      final startDate = DateTime.parse(care['start_date']);
                      final endDate = DateTime.parse(care['end_date']);

                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(12),
                          leading: Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              color: Colors.grey[200],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: plant != null && plant['photo'] != null
                                ? ClipRRect(
                                    borderRadius: BorderRadius.circular(8),
                                    child: Image.network(
                                      plant['photo'],
                                      fit: BoxFit.cover,
                                      errorBuilder: (context, error, stackTrace) {
                                        return Icon(
                                          Icons.local_florist,
                                          size: 25,
                                          color: Colors.green[700],
                                        );
                                      },
                                    ),
                                  )
                                : Icon(
                                    Icons.local_florist,
                                    size: 25,
                                    color: Colors.green[700],
                                  ),
                          ),
                          title: Text(
                            plant != null ? plant['nom'] : 'Plante inconnue',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(plant != null ? (plant['espece'] ?? 'Espèce non spécifiée') : 'Espèce inconnue'),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  Icon(
                                    Icons.calendar_today,
                                    size: 14,
                                    color: Colors.green[700],
                                  ),
                                  const SizedBox(width: 4),
                                  Expanded(
                                    child: Text(
                                      'Du ${formatDateNumber(startDate.day)}/${formatDateNumber(startDate.month)} au ${formatDateNumber(endDate.day)}/${formatDateNumber(endDate.month)}',
                                      style: const TextStyle(fontSize: 12),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          onTap: () async {
                            final result = await Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => PlantCareDetailsScreen(
                                  isCurrentPlant: false,
                                  careId: care['id'],
                                ),
                              ),
                            );
                            if (result == true) {
                              await _loadPendingCares();
                            }
                          },
                        ),
                      );
                    },
                  ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const AddPlantScreen(),
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                    ),
                    child: const Text(
                      'Créer une annonce de garde',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
      currentIndex: 0,
    );
  }
}
