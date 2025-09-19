import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:mobile/views/plant_care_details_screen.dart';
import 'package:mobile/services/plant_care_service.dart';
import '../widgets/adaptive_image.dart';

class PlantCurrentListScreen extends StatefulWidget {
  const PlantCurrentListScreen({super.key});

  @override
  PlantCurrentListScreenState createState() => PlantCurrentListScreenState();
}

class PlantCurrentListScreenState extends State<PlantCurrentListScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  // Contrôleur pour gérer l'input de recherche
  final TextEditingController _searchController = TextEditingController();
  // Stockage de la requête filtrée en minuscules
  String _searchQuery = "";
  late final PlantCareService _plantCareService;
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
      // Services initialization
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
    if (!_isInitialized) {
      return;
    }

    try {
      setState(() {
        isLoading = true;
        error = null;
      });

      // Charger mes plantes confiées (je suis propriétaire)
      final myOwnedPlantCares = await _plantCareService.getMyPlantCares();

      // Charger les plantes que je garde (je suis gardien)
      final myCaretakingPlants = await _plantCareService.getMyCaretakingPlants();

      // Logs pour déboguer
      for (var care in myOwnedPlantCares) {
        final plant = care['plant'];
        if (plant != null) {
        }
      }

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

  // === NETTOYAGE DES RESSOURCES ===
  @override
  void dispose() {
    _tabController.dispose();
    // Nettoyage obligatoire du contrôleur pour éviter les fuites mémoire
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
            // === BARRE DE RECHERCHE ===
            child: TextField(
              controller: _searchController,
              // Mise à jour en temps réel à chaque frappe
              onChanged: (value) {
                setState(() {
                  // Normalisation en minuscules pour recherche insensible à la casse
                  _searchQuery = value.toLowerCase();
                });
              },
              decoration: InputDecoration(
                hintText: "Recherche",
                prefixIcon: const Icon(Icons.search),
                // Bouton croix pour effacer la recherche
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          setState(() {
                            _searchQuery = "";
                          });
                        },
                      )
                    : null,
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

    // === LOGIQUE DE FILTRAGE ===
    // Filtrage sécurisé avec vérifications null
    final filteredCares = sortedCares
        .where((care) =>
          care['plant'] != null &&
          care['plant']['name'] != null &&
          care['plant']['name'].toLowerCase().contains(_searchQuery))
        .toList();

    // Gestion du cas vide
    if (filteredCares.isEmpty) {
      return const Center(child: Text('Aucune plante confiée'));
    }

    // Affichage de la liste des gardes sous forme de liste
    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredCares.length,              // Nombre total de gardes filtrées à afficher
      itemBuilder: (context, index) {               // Construction de chaque carte de garde (appelée pour chaque élément)
        final care = filteredCares[index];
        final plant = care['plant'];
        final startDate = DateTime.parse(care['start_date']);
        final endDate = DateTime.parse(care['end_date']);
        final owner = care['owner'];

        return Column(
          children: [
            Stack(
              children: [
                ListTile(
                  // Photo de la plante
                  leading: CircleAvatar(
                    backgroundColor: Colors.grey[200],
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(50),
                      child: AdaptiveImage(
                        imageBase64: plant['photo_base64'],
                        width: 40,
                        height: 40,
                        fit: BoxFit.cover,
                        errorWidget: Icon(
                          Icons.local_florist,
                          color: Colors.green[700],
                        ),
                      ),
                    ),
                  ),
                  // Nom de la plante
                  title: Text(plant['name'] ?? 'Plante'),
                  // Propriétaire et dates de garde
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Propriétaire: ${owner['first_name']} ${owner['last_name']}'),
                      Text('Du ${DateFormat('dd/MM/yy').format(startDate)} au ${DateFormat('dd/MM/yy').format(endDate)}'),
                      if (care['location'] != null)  // Affichage conditionnel
                        Text('Lieu: ${care['location']}',
                          style: const TextStyle(fontSize: 12, color: Colors.grey)),
                    ],
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  // Navigation vers la page de détails de la garde
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
                // Badge de statut en haut à droite
                Positioned(
                  top: 8,
                  right: 8,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getStatusColor(care['status']),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _getStatusText(care['status']),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const Divider(),
          ],
        );
      },
    );
  }

  Widget _buildMyCaretakingList() {
    // === FILTRAGE ONGLET 2 ===
    // Même logique de filtrage appliquée au second onglet
    final filteredCares = mesCaretaking
        .where((care) =>
          care['plant'] != null &&
          care['plant']['name'] != null &&
          care['plant']['name'].toLowerCase().contains(_searchQuery))
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
            Stack(
              children: [
                ListTile(
                  // Photo de la plante
                  leading: CircleAvatar(
                    backgroundColor: Colors.grey[200],
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(50),
                      child: AdaptiveImage(
                        imageBase64: plant['photo_base64'],
                        width: 40,
                        height: 40,
                        fit: BoxFit.cover,
                        errorWidget: Icon(
                          Icons.local_florist,
                          color: Colors.green[700],
                        ),
                      ),
                    ),
                  ),
                  // Nom de la plante
                  title: Text(plant['name'] ?? 'Plante'),
                  // Espèce et dates de garde
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(plant['species'] ?? 'Espèce non spécifiée'),
                      Text('Du ${DateFormat('dd/MM/yy').format(startDate)} au ${DateFormat('dd/MM/yy').format(endDate)}'),
                    ],
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  // Navigation vers la page de détails de la garde
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
                // Badge de statut en haut à droite
                Positioned(
                  top: 8,
                  right: 8,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getStatusColor(care['status']),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _getStatusText(care['status']),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const Divider(),
          ],
        );
      },
    );
  }

  // Fonction helper pour les couleurs de statut
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Colors.orange;
      case 'accepted':
        return Colors.blue;
      case 'in_progress':
        return Colors.green;
      case 'completed':
        return Colors.purple;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  // Fonction helper pour les textes de statut
  String _getStatusText(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'En attente';
      case 'accepted':
        return 'Acceptée';
      case 'in_progress':
        return 'En cours';
      case 'completed':
        return 'Terminée';
      case 'cancelled':
        return 'Annulée';
      default:
        return status;
    }
  }
}
