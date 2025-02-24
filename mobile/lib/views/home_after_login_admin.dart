import 'package:flutter/material.dart';
import 'base_page_botaniste.dart';
import 'plant_detail_botaniste.dart';

class HomeAfterLoginAdmin extends StatefulWidget {
  const HomeAfterLoginAdmin({super.key});

  @override
  State<HomeAfterLoginAdmin> createState() => _HomeAfterLoginAdminState();
}

class _HomeAfterLoginAdminState extends State<HomeAfterLoginAdmin> {
  final TextEditingController _searchController = TextEditingController();

  Widget _buildPlantCard(BuildContext context, int index) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const PlantDetailBotaniste(),
          ),
        );
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
                child: Center(
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
                      'Plante ${index + 1}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '2 km',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
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

  @override
  Widget build(BuildContext context) {
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
              // Barre de recherche
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
                        // Ajouter la logique de filtrage ici
                      },
                    ),
                  ),
                  onChanged: (value) {
                    // Ajouter la logique de recherche ici
                    setState(() {
                      // Mettre à jour la liste des plantes en fonction de la recherche
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
                    onPressed: () {
                      // Ajouter la logique pour voir toutes les plantes
                    },
                    child: const Text(
                      'Voir tout',
                      style: TextStyle(color: Colors.green),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                children: List.generate(
                  4,
                  (index) => _buildPlantCard(context, index),
                ),
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
