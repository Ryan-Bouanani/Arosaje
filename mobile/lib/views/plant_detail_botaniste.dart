import 'package:flutter/material.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/services/advice_service.dart';
import 'package:mobile/models/plant.dart';

class PlantDetailBotaniste extends StatefulWidget {
  final int plantId;
  
  const PlantDetailBotaniste({
    super.key,
    required this.plantId,
  });

  @override
  State<PlantDetailBotaniste> createState() => _PlantDetailBotanisteState();
}

class _PlantDetailBotanisteState extends State<PlantDetailBotaniste> {
  late final PlantService _plantService;
  late final AdviceService _adviceService;
  bool _isLoading = true;
  String? _error;
  Plant? _plant;
  List<Map<String, dynamic>> _advices = [];
  final TextEditingController _commentController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      _plantService = await PlantService.init();
      _adviceService = await AdviceService.init();
      await _loadData();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadData() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final plant = await _plantService.getPlantDetails(widget.plantId);
      final advices = await _adviceService.getMyAdvices();
      
      if (mounted) {
        setState(() {
          _plant = plant;
          _advices = advices.where((advice) => advice['plant_id'] == widget.plantId).toList();
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

  Future<void> _submitComment() async {
    if (_commentController.text.isEmpty) return;

    try {
      await _adviceService.createAdvice(
        plantId: widget.plantId,
        texte: _commentController.text,
      );
      
      _commentController.clear();
      Navigator.of(context).pop();
      
      // Recharger les conseils
      await _loadData();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Conseil ajouté avec succès'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur lors de l\'ajout du conseil: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showCommentDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text(
            'Rédiger un conseil',
            style: TextStyle(color: Color(0xFF1B4332)),
          ),
          content: TextField(
            controller: _commentController,
            decoration: const InputDecoration(
              hintText: 'Écrivez votre conseil ici...',
              border: OutlineInputBorder(),
              focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.green),
              ),
            ),
            maxLines: 4,
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _commentController.clear();
              },
              child: const Text(
                'Annuler',
                style: TextStyle(color: Colors.grey),
              ),
            ),
            ElevatedButton(
              onPressed: _submitComment,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
              ),
              child: const Text('Valider'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildBotanistComments() {
    if (_advices.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Conseils des botanistes',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              'Aucun conseil pour le moment',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Conseils des botanistes',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        for (var advice in _advices) ...[
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  advice['texte'],
                  style: const TextStyle(fontSize: 14),
                ),
                const SizedBox(height: 8),
                Text(
                  'Statut: ${advice['status']}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
        ],
      ],
    );
  }

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
          color: Colors.black,
        ),
        title: Text(
          _plant?.nom ?? 'Détail de la plante',
          style: const TextStyle(color: Colors.black, fontSize: 18),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text('Erreur: $_error'))
              : _plant == null
                  ? const Center(child: Text('Plante non trouvée'))
                  : RefreshIndicator(
                      onRefresh: _loadData,
                      child: SingleChildScrollView(
                        physics: const AlwaysScrollableScrollPhysics(),
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Owner Section
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.grey[100],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Row(
                                  children: [
                                    CircleAvatar(
                                      backgroundColor: Colors.grey,
                                      child: Icon(Icons.person, color: Colors.white),
                                    ),
                                    SizedBox(width: 16),
                                    Text(
                                      'Propriétaire',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              const SizedBox(height: 24),

                              // Plant Image Section
                              const Text(
                                'Photo de la plante',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 8),
                              Container(
                                width: double.infinity,
                                height: 200,
                                decoration: BoxDecoration(
                                  color: Colors.grey[200],
                                  borderRadius: BorderRadius.circular(8),
                                  image: _plant?.photo != null
                                      ? DecorationImage(
                                          image: NetworkImage(_plant!.photo!),
                                          fit: BoxFit.cover,
                                        )
                                      : null,
                                ),
                                child: _plant?.photo == null
                                    ? const Center(
                                        child: Icon(
                                          Icons.image,
                                          size: 50,
                                          color: Colors.grey,
                                        ),
                                      )
                                    : null,
                              ),

                              const SizedBox(height: 24),

                              // Plant Details Section
                              const Text(
                                'Détails de la plante',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.grey[100],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text('Nom: ${_plant?.nom ?? 'Non spécifié'}'),
                                    if (_plant?.espece != null)
                                      Text('Espèce: ${_plant!.espece}'),
                                    if (_plant?.description != null)
                                      Text('Description: ${_plant!.description}'),
                                  ],
                                ),
                              ),

                              const SizedBox(height: 24),

                              // Botanist Comments Section
                              _buildBotanistComments(),
                            ],
                          ),
                        ),
                      ),
                    ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ElevatedButton(
          onPressed: _showCommentDialog,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            padding: const EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text(
            'Rédiger un conseil',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
