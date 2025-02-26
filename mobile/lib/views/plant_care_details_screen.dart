import 'package:flutter/material.dart';
import 'package:mobile/views/add_report_screen.dart';
import 'package:mobile/services/plant_care_service.dart';

class PlantCareDetailsScreen extends StatefulWidget {
  final bool isCurrentPlant;
  final int? careId;
  final int? plantId;

  const PlantCareDetailsScreen({
    super.key,
    required this.isCurrentPlant,
    this.careId,
    this.plantId,
  }) : assert(careId != null || plantId != null, 'Either careId or plantId must be provided');

  @override
  State<PlantCareDetailsScreen> createState() => _PlantCareDetailsScreenState();
}

class _PlantCareDetailsScreenState extends State<PlantCareDetailsScreen> {
  late final PlantCareService _plantCareService;
  Map<String, dynamic>? _careDetails;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  Future<void> _initializeService() async {
    try {
      _plantCareService = await PlantCareService.init();
      await _loadCareDetails();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadCareDetails() async {
    try {
      final details = widget.careId != null 
          ? await _plantCareService.getPlantCareDetails(widget.careId!)
          : await _plantCareService.getPlantCareDetailsByPlantId(widget.plantId!);
      setState(() {
        _careDetails = details;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _acceptCare() async {
    try {
      setState(() => _isLoading = true);
      if (widget.careId == null) {
        throw Exception('Cannot accept care without a care ID');
      }
      await _plantCareService.acceptPlantCare(widget.careId!);
      Navigator.pop(context, true);
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
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
          _careDetails != null ? _careDetails!['plant']['nom'] : 'Chargement...',
          style: const TextStyle(color: Colors.black, fontSize: 18),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : SingleChildScrollView(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Owner Section
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const CircleAvatar(
                              backgroundColor: Colors.grey,
                              child: Icon(Icons.person, color: Colors.white),
                            ),
                            const SizedBox(width: 16),
                            Text(
                              _careDetails?['owner']?['username'] ?? 'Propriétaire inconnu',
                              style: const TextStyle(fontSize: 14),
                            ),
                          ],
                        ),

                        const SizedBox(height: 16),

                        // Action Buttons
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () {},
                                icon: const Icon(Icons.local_florist, color: Colors.green),
                                label: const Text(
                                  'Demander un conseil botaniste',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(fontSize: 12),
                                ),
                                style: OutlinedButton.styleFrom(
                                  padding: const EdgeInsets.all(12),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () {},
                                icon: const Icon(Icons.message, color: Colors.black),
                                label: const Text(
                                  'Contacter le propriétaire',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(fontSize: 12),
                                ),
                                style: OutlinedButton.styleFrom(
                                  padding: const EdgeInsets.all(12),
                                ),
                              ),
                            ),
                          ],
                        ),

                        const SizedBox(height: 24),

                        // Plant Info Section
                        const Text(
                          'Informations Clés sur la Plante',
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
                              Text('Localisation: ${_careDetails?['localisation'] ?? 'Non spécifiée'}'),
                              if (_careDetails?['plant']?['espece'] != null)
                                Text('Espèce: ${_careDetails?['plant']?['espece']}'),
                            ],
                          ),
                        ),

                        const SizedBox(height: 24),

                        // Plant Image Section
                        const Text(
                          'Image de la Plante',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          width: double.infinity,
                          height: 200,
                          decoration: BoxDecoration(
                            color: Colors.grey[200],
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: _careDetails?['plant']?['photo'] != null
                              ? ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: Image.network(
                                    _careDetails?['plant']?['photo'] ?? '',
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) {
                                      return const Center(
                                        child: Icon(Icons.error_outline, size: 40, color: Colors.grey),
                                      );
                                    },
                                  ),
                                )
                              : const Center(
                                  child: Icon(Icons.image_not_supported, size: 40, color: Colors.grey),
                                ),
                        ),

                        const SizedBox(height: 16),
                        Text(
                          _careDetails!['plant']['nom'],
                          style: const TextStyle(fontSize: 14),
                        ),
                        Text(
                          'Type de Plante: ${_careDetails!['plant']['espece'] ?? 'Non spécifié'}',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),

                        const SizedBox(height: 24),

                        // Instructions Section
                        const Text(
                          'Instructions du propriétaire',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              const CircleAvatar(
                                radius: 16,
                                backgroundColor: Colors.grey,
                                child: Icon(Icons.person, color: Colors.white, size: 20),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _careDetails?['owner']?['username'] ?? 'Propriétaire inconnu',
                                      style: const TextStyle(fontWeight: FontWeight.bold)
                                    ),
                                    Text(_careDetails?['care_instructions'] ?? 'Aucune instruction spécifique'),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 24),
                      ],
                    ),
                  ),
                ),
      bottomNavigationBar: widget.isCurrentPlant
          ? Padding(
              padding: const EdgeInsets.all(16.0),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const RapportDeGarde(),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Faire un rapport',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            )
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: ElevatedButton(
                onPressed: _acceptCare,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Prendre la garde',
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