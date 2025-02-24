import 'package:flutter/material.dart';
import 'base_page.dart';

class PlantHistoryScreen extends StatelessWidget {
  const PlantHistoryScreen({super.key});

  Widget _buildPlantList(String title, List<Map<String, String>> plants) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: 8),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: plants.length,
          separatorBuilder: (context, index) => const Divider(height: 1),
          itemBuilder: (context, index) {
            final plant = plants[index];
            return ListTile(
              leading: const Icon(
                Icons.local_florist,
                color: Colors.green,
              ),
              title: Text(
                plant['name']!,
                style: const TextStyle(
                  fontWeight: FontWeight.w500,
                ),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(plant['owner']!),
                  Text(plant['period']!),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 16),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final plantsGardees = [
      {
        'name': 'Monstera',
        'owner': 'Marie Dupont',
        'period': 'Du 15/09 au 30/09',
      },
      {
        'name': 'Ficus Lyrata',
        'owner': 'Pierre Lambert',
        'period': 'Du 20/09 au 05/10',
      },
    ];

    final plantsConfiees = [
      {
        'name': 'Monstera',
        'owner': 'Marie Dupont',
        'period': 'Du 15/09 au 30/09',
      },
      {
        'name': 'Ficus Lyrata',
        'owner': 'Pierre Lambert',
        'period': 'Du 20/09 au 05/10',
      },
    ];

    return BasePage(
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(16, 40, 16, 20),
              child: const Text(
                'Mes Plantes',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
                ),
                textAlign: TextAlign.left,
              ),
            ),
            _buildPlantList(
                'Liste des Plantes Gardées En Cours', plantsGardees),
            const SizedBox(height: 8),
            _buildPlantList(
                'Liste des Plantes Confiées En Cours', plantsConfiees),
          ],
        ),
      ),
      currentIndex: 1,
    );
  }
}
