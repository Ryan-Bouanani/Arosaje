import 'package:flutter/material.dart';
import 'package:mobile/views/plant_care_details_screen.dart';

class PlantHistoryScreen extends StatefulWidget {
  const PlantHistoryScreen({super.key});

  @override
  _PlantHistoryScreenState createState() => _PlantHistoryScreenState();
}

class _PlantHistoryScreenState extends State<PlantHistoryScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = "";

  final List<Map<String, String>> plantsConfiees = [
    {'name': 'Plante A', 'type': 'Rose rouge', 'date': '10/15/2021', 'gardien': 'Marie', 'image': 'assets/monstera.webp'},
    {'name': 'Plante B', 'type': 'Lys blanc', 'date': '09/27/2021', 'gardien': 'Jean', 'image': 'assets/ficus.png'},
    {'name': 'Plante C', 'type': 'Orchidée violette', 'date': '08/02/2021', 'gardien': 'Sophie', 'image': 'assets/monstera.webp'},
  ];

  final List<Map<String, String>> plantsGardees = [
    {'name': 'Plante D', 'type': 'Ficus', 'date': '11/05/2021', 'gardien': 'Paul', 'image': 'assets/ficus.png'},
    {'name': 'Plante E', 'type': 'Cactus', 'date': '07/19/2021', 'gardien': 'Emma', 'image': 'assets/monstera.webp'},
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
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
            icon: const Icon(Icons.notifications),
            onPressed: () {},
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
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildPlantList(plantsConfiees),
                _buildPlantList(plantsGardees),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlantList(List<Map<String, String>> plants) {
    final filteredPlants = plants
        .where((plant) => plant['name']!.toLowerCase().contains(_searchQuery))
        .toList();

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: filteredPlants.length,
      itemBuilder: (context, index) {
        final plant = filteredPlants[index];
        return Column(
          children: [
            ListTile(
              leading: CircleAvatar(
                backgroundImage: AssetImage(plant['image']!),
                backgroundColor: Colors.grey[200],
              ),
              title: Text(
                plant['name']!,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text(plant['type']!),
              trailing: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    "Date: ${plant['date']}",
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text("Gardien: ${plant['gardien']}"),
                ],
              ),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const PlantCareDetailsScreen(isCurrentPlant: false),
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
