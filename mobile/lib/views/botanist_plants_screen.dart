import 'package:flutter/material.dart';
import 'package:mobile/services/advice_service.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/models/plant.dart';
import 'base_page_botaniste.dart';

class BotanistPlantsScreen extends StatefulWidget {
  const BotanistPlantsScreen({super.key});

  @override
  State<BotanistPlantsScreen> createState() => _BotanistPlantsScreenState();
}

class _BotanistPlantsScreenState extends State<BotanistPlantsScreen> {
  late final AdviceService _adviceService;
  late final PlantService _plantService;
  List<Plant> _allPlants = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      _adviceService = await AdviceService.init();
      _plantService = await PlantService.init();
      await _loadAllPlants();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadAllPlants() async {
    try {
      final plants = await _plantService.getAllPlants();
      setState(() {
        _allPlants = plants;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _showAddAdviceDialog(Plant plant) async {
    final TextEditingController adviceController = TextEditingController();
    
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Conseil pour ${plant.nom}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Espèce: ${plant.espece ?? 'Non spécifié'}'),
            const SizedBox(height: 16),
            TextField(
              controller: adviceController,
              maxLines: 5,
              decoration: const InputDecoration(
                labelText: 'Votre conseil',
                hintText: 'Entrez votre conseil pour cette plante...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Annuler'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (adviceController.text.trim().isNotEmpty) {
                try {
                  await _adviceService.createAdvice(
                    plantId: plant.id,
                    texte: adviceController.text.trim(),
                  );
                  Navigator.of(context).pop(true);
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Erreur: ${e.toString()}'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            child: const Text('Ajouter le conseil'),
          ),
        ],
      ),
    );

    if (result == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Conseil ajouté avec succès !'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return BasePageBotaniste(
      currentIndex: 1,
      body: Scaffold(
        appBar: AppBar(
          title: const Text('Catalogue des Plantes'),
          backgroundColor: Colors.green,
          foregroundColor: Colors.white,
        ),
        body: _error != null
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(_error!, style: const TextStyle(color: Colors.red)),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loadAllPlants,
                      child: const Text('Réessayer'),
                    ),
                  ],
                ),
              )
            : _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _allPlants.isEmpty
                    ? const Center(
                        child: Text('Aucune plante disponible.'),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _allPlants.length,
                        itemBuilder: (context, index) {
                          final plant = _allPlants[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ListTile(
                              leading: const CircleAvatar(
                                backgroundColor: Colors.green,
                                child: Icon(Icons.local_florist, color: Colors.white),
                              ),
                              title: Text(plant.nom),
                              subtitle: Text('Espèce: ${plant.espece ?? 'Non spécifiée'}'),
                              trailing: ElevatedButton.icon(
                                onPressed: () => _showAddAdviceDialog(plant),
                                icon: const Icon(Icons.add_comment, size: 16),
                                label: const Text('Conseil'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.green,
                                  foregroundColor: Colors.white,
                                ),
                              ),
                            ),
                          );
                        },
                      ),
      ),
    );
  }
}
