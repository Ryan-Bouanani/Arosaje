import 'package:flutter/material.dart';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile/services/care_report_service.dart';

// Import conditionnel pour File (éviter sur web)
import 'dart:io' if (dart.library.html) 'dart:io' show File;

class RapportDeGarde extends StatefulWidget {
  final int? plantCareId;
  
  const RapportDeGarde({super.key, this.plantCareId});

  @override
  _RapportDeGardeState createState() => _RapportDeGardeState();
}

class _RapportDeGardeState extends State<RapportDeGarde> {
  dynamic _imageFile; // File sur mobile, null sur web
  Uint8List? _webImage;
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _descriptionController = TextEditingController();
  
  late final CareReportService _careReportService;
  bool _isLoading = false;
  bool _isInitialized = false;

  // Valeurs pour les listes déroulantes
  String _hydratationLevel = 'Moyen';
  String _vitaliteLevel = 'Moyen';
  String _santePlante = 'Moyen';

  // Liste des options disponibles
  final List<String> _niveaux = ['Bas', 'Moyen', 'Bon'];

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  Future<void> _initializeService() async {
    try {
      _careReportService = await CareReportService.init();
      setState(() {
        _isInitialized = true;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur d\'initialisation: ${e.toString()}')),
      );
    }
  }

  Future<void> _pickImage() async {
    final XFile? pickedFile =
        await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      if (kIsWeb) {
        // Pour le web, lire les bytes de l'image
        final bytes = await pickedFile.readAsBytes();
        setState(() {
          _webImage = bytes;
          _imageFile = null; // Clear mobile file
        });
      } else {
        // Pour mobile, utiliser File
        if (!kIsWeb) {
          setState(() {
            _imageFile = File(pickedFile.path);
            _webImage = null; // Clear web bytes
          });
        }
      }
    }
  }

  Future<void> _submitReport() async {
    if (widget.plantCareId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Erreur: ID de garde manquant')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // Créer le rapport
      final report = await _careReportService.createCareReport(
        plantCareId: widget.plantCareId!,
        healthLevel: _santePlante,
        hydrationLevel: _hydratationLevel,
        vitalityLevel: _vitaliteLevel,
        description: _descriptionController.text.trim().isNotEmpty 
            ? _descriptionController.text.trim() 
            : null,
      );

      // Upload la photo si sélectionnée
      if (kIsWeb && _webImage != null) {
        final photoResult = await _careReportService.uploadCareReportPhoto(
          report['id'],
          _webImage!, // Pass bytes for web
        );
      } else if (!kIsWeb && _imageFile != null) {
        final photoResult = await _careReportService.uploadCareReportPhoto(
          report['id'],
          _imageFile!.path, // Pass path for mobile
        );
      }

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Rapport de séance envoyé avec succès !'),
          backgroundColor: Colors.green,
        ),
      );

      Navigator.pop(context, true); // Retourner avec succès
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _getImageWidget() {
    if (kIsWeb && _webImage != null) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(8.0),
        child: Image.memory(
          _webImage!,
          fit: BoxFit.cover,
        ),
      );
    } else if (!kIsWeb && _imageFile != null) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(8.0),
        child: Image.file(
          _imageFile as File,
          fit: BoxFit.cover,
        ),
      );
    } else {
      return const Center(
        child: Text('Aucune image sélectionnée'),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Rapports de Garde'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Zone d'image
            Container(
              height: 300,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8.0),
              ),
              child: _getImageWidget(),
            ),

            // Bouton pour ajouter une photo
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16.0),
              child: ElevatedButton.icon(
                onPressed: _pickImage,
                icon: const Icon(Icons.add_photo_alternate),
                label: const Text('Ajouter une photo'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12.0),
                ),
              ),
            ),

            // Champs d'information avec listes déroulantes
            Card(
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Santé de la Plante'),
                    const SizedBox(height: 4),
                    DropdownButton<String>(
                      value: _hydratationLevel,
                      isExpanded: true,
                      items: _niveaux.map((String value) {
                        return DropdownMenuItem<String>(
                          value: value,
                          child: Text(value),
                        );
                      }).toList(),
                      onChanged: (String? newValue) {
                        setState(() {
                          _hydratationLevel = newValue!;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Niveau d\'Hydratation'),              
                    const SizedBox(height: 4),
                    DropdownButton<String>(
                      value: _vitaliteLevel,
                      isExpanded: true,
                      items: _niveaux.map((String value) {
                        return DropdownMenuItem<String>(
                          value: value,
                          child: Text(value),
                        );
                      }).toList(),
                      onChanged: (String? newValue) {
                        setState(() {
                          _vitaliteLevel = newValue!;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Vitalité Générale'),
                    const SizedBox(height: 4),
                    DropdownButton<String>(
                      value: _santePlante,
                      isExpanded: true,
                      items: _niveaux.map((String value) {
                        return DropdownMenuItem<String>(
                          value: value,
                          child: Text(value),
                        );
                      }).toList(),
                      onChanged: (String? newValue) {
                        setState(() {
                          _santePlante = newValue!;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),

            // Champ de description
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              maxLines: 4,
              decoration: InputDecoration(
                labelText: 'Description détaillée',
                hintText: 'Ajoutez vos commentaires ici...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
                filled: true,
                fillColor: Colors.white,
              ),
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ElevatedButton(
          onPressed: _isLoading || !_isInitialized ? null : _submitReport,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            padding: const EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: _isLoading 
            ? const CircularProgressIndicator(color: Colors.white)
            : const Text(
            'Envoyer le rapport de séance',
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

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }
}
