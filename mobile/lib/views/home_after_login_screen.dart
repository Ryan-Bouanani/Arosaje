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
  bool _locationLoading = true;

  // Liste des gardes disponibles (remplace les données hardcodées)
  List<Map<String, dynamic>> _availableCares = [];
  

  // Point central de la carte (Toujours le centre de la France)
  LatLng get _center => const LatLng(46.7, 2.2);

  String formatDateNumber(int number) {
    return number.toString().padLeft(2, '0');
  }

  String _formatDate(String? dateString) {
    if (dateString == null) return '';
    try {
      final date = DateTime.parse(dateString);
      return '${formatDateNumber(date.day)}/${formatDateNumber(date.month)}/${date.year}';
    } catch (e) {
      return dateString;
    }
  }

  @override
  void initState() {
    super.initState();
    _initializeService();
    _getUserLocationWithTimeout();
  }

  Future<void> _getUserLocationWithTimeout() async {
    try {
      // Essayer d'obtenir la position avec timeout de 8 secondes
      await Future.any([
        _getUserLocation(),
        Future.delayed(const Duration(seconds: 8)),
      ]);
    } catch (e) {
      print("Timeout ou erreur géolocalisation: $e");
    } finally {
      // Toujours arrêter le loading après 8 secondes max
      if (mounted) {
        setState(() {
          _locationLoading = false;
        });
      }
    }
  }

  Future<void> _getUserLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() {
          _locationLoading = false;
        });
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() {
            _locationLoading = false;
          });
          return;
        }
      }
      if (permission == LocationPermission.deniedForever) {
        setState(() {
          _locationLoading = false;
        });
        return;
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 6),
      );

      if (mounted) {
        setState(() {
          _userLocation = LatLng(position.latitude, position.longitude);
          _locationLoading = false;
        });
      }
    } catch (e) {
      print("Erreur localisation: $e");
      if (mounted) {
        setState(() {
          _locationLoading = false;
        });
      }
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
          // Convertir les gardes réelles au format map avec localisation
          _availableCares = _convertCaresToMapFormat(cares);
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

  // Convertir les gardes API au format attendu par la carte
  List<Map<String, dynamic>> _convertCaresToMapFormat(List<Map<String, dynamic>> cares) {
    return cares.map((care) {
      LatLng location;
      
      // Utiliser les vraies coordonnées si disponibles
      if (care['latitude'] != null && care['longitude'] != null) {
        location = LatLng(
          care['latitude'].toDouble(),
          care['longitude'].toDouble(),
        );
      } else {
        // Fallback sur centre de la France par défaut si pas de coordonnées
        location = const LatLng(46.7, 2.2);
        print('Garde ${care['id']} sans coordonnées, utilisation du centre de la France par défaut');
      }
      
      return {
        'id': care['id'],
        'plant': care['plant'],
        'location': location,
        'localisation': care['localisation'] ?? 'Localisation non spécifiée',
        'care_instructions': care['care_instructions'] ?? 'Aucune instruction spécifique',
        'start_date': care['start_date'],
        'end_date': care['end_date'],
        'owner': care['owner'],
        'status': care['status'],
      };
    }).toList();
  }

  // Récupérer les plantes à afficher (vraies gardes uniquement)
  List<Map<String, dynamic>> _getPlantsToShow() {
    return _availableCares;
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
        child: _locationLoading
          ? Container(
              color: Colors.grey[100],
              child: const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(
                      color: Colors.green,
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Localisation en cours...',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 16,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Centrage sur votre position',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            )
          : FlutterMap(
              options: MapOptions(
                initialCenter: _center, // Toujours centré sur la France
                initialZoom: 5.0, // Vue France complète incluant Lille
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
                    ..._getPlantsToShow()
                        .map(
                          (care) => Marker(
                            point: care['location'],
                            width: 40,
                            height: 40,
                            child: GestureDetector(
                              onTap: () {
                                _showPlantDetails(care);
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

  // Afficher les détails d'une garde disponible
  void _showPlantDetails(Map<String, dynamic> care) {
    final plant = care['plant'] ?? {};
    final owner = care['owner'] ?? {};
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
                          plant['nom'] ?? 'Plante inconnue',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                        Text(
                          'de ${owner['prenom'] ?? ''} ${owner['nom'] ?? 'Propriétaire'}',
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                            color: Colors.blue,
                          ),
                        ),
                        Text(
                          plant['espece'] ?? 'Espèce inconnue',
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
                      care['localisation'] ?? 'Localisation non spécifiée',
                      style: TextStyle(color: Colors.grey[800]),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // Dates de garde
              if (care['start_date'] != null && care['end_date'] != null) ...[
                Row(
                  children: [
                    Icon(Icons.calendar_today, color: Colors.green[700], size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '${_formatDate(care['start_date'])} - ${_formatDate(care['end_date'])}',
                        style: TextStyle(
                          color: Colors.grey[800],
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
              ],
              // Instructions
              if (care['care_instructions'] != null && care['care_instructions'].toString().isNotEmpty) ...[
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.info_outline, color: Colors.green[700], size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        care['care_instructions'],
                        style: TextStyle(color: Colors.grey[800]),
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
              ],
              // Statut
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.green[100],
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'DISPONIBLE',
                  style: TextStyle(
                    color: Colors.green[700],
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    // Naviguer vers les détails de la garde
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
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                  ),
                  child: const Text('Proposer de garder'),
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
          itemCount: _getPlantsToShow().length,
          itemBuilder: (context, index) {
            final care = _getPlantsToShow()[index];
            final plant = care['plant'] ?? {};
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
                  plant['nom'] ?? 'Plante inconnue',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('${plant['espece'] ?? 'Espèce inconnue'} - ${(care['owner'] != null) ? '${care['owner']['prenom']} ${care['owner']['nom']}' : 'Propriétaire inconnu'}'),
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
                            care['localisation'] ?? 'Localisation non spécifiée',
                            style: const TextStyle(fontSize: 12),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                onTap: () => _showPlantDetails(care),
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
                  'Gardes disponibles près de chez vous',
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
                      'Demandes de garde actives',
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
                    onPressed: () async {
                      final result = await Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const AddPlantScreen(),
                        ),
                      );
                      if (result == true) {
                        setState(() {
                          _loadPendingCares();
                        });
                      }
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
