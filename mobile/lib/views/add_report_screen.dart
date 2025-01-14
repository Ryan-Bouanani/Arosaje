import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';

class RapportDeGarde extends StatefulWidget {
  const RapportDeGarde({super.key});

  @override
  _RapportDeGardeState createState() => _RapportDeGardeState();
}

class _RapportDeGardeState extends State<RapportDeGarde> {
  File? _imageFile;
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _descriptionController = TextEditingController();

  // Valeurs pour les listes déroulantes
  String _hydratationLevel = 'Moyen';
  String _vitaliteLevel = 'Moyen';
  String _santePlante = 'Moyen';

  // Liste des options disponibles
  final List<String> _niveaux = ['Bas', 'Moyen', 'Bon'];

  Future<void> _pickImage() async {
    final XFile? pickedFile =
        await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _imageFile = File(pickedFile.path);
      });
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
              child: _imageFile != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(8.0),
                      child: Image.file(
                        _imageFile!,
                        fit: BoxFit.cover,
                      ),
                    )
                  : const Center(
                      child: Text('Aucune image sélectionnée'),
                    ),
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
                    const Text('Niveau d\'Hydratation'),
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
                    const Text('Vitalité Générale'),
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
                    const Text('Santé de la Plante'),
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
          onPressed: () {
            // Action à effectuer lors de l'envoi du rapport
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            padding: const EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text(
            'Envoyer le rapport',
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
