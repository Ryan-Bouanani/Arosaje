import 'package:flutter/material.dart';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/services/plant_care_service.dart';
import 'package:mobile/widgets/address_autocomplete_field.dart';
import 'package:mobile/views/plant_care_details_screen.dart';
import 'package:intl/intl.dart';

// Import conditionnel pour File (éviter sur web)
import 'dart:io' if (dart.library.html) 'dart:io' show File;

class AddPlantScreen extends StatefulWidget {
  const AddPlantScreen({Key? key}) : super(key: key);

  @override
  State<AddPlantScreen> createState() => _AddPlantScreenState();
}

class _AddPlantScreenState extends State<AddPlantScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isFirstStep = true;
  dynamic _imageFile; // File sur mobile, null sur web
  Uint8List? _webImage;
  String? _originalFileName; // Nom du fichier original avec extension
  late PlantService _plantService;
  late PlantCareService _plantCareService;
  int? _createdPlantId;

  // Contrôleurs pour les champs de la plante
  final _nomController = TextEditingController();
  final _especeController = TextEditingController();

  // Contrôleurs pour les champs de la garde
  final _localisationController = TextEditingController();
  final _careInstructionsController = TextEditingController();
  DateTime? _startDate;
  DateTime? _endDate;
  final DateFormat _dateFormat = DateFormat('dd/MM/yyyy', 'fr_FR');

  @override
  void initState() {
    super.initState();
    _initServices();
  }

  void _initServices() async {
    _plantService = await PlantService.init();
    _plantCareService = await PlantCareService.init();
  }

  @override
  void dispose() {
    _nomController.dispose();
    _especeController.dispose();
    _localisationController.dispose();
    _careInstructionsController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final pickedFile = await ImagePicker().pickImage(source: source);
    if (pickedFile != null) {
      setState(() {
        _originalFileName = pickedFile.name; // Stocker le nom original avec extension
      });
      
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

  Future<void> _selectDateRange(BuildContext context) async {
    final DateTimeRange? picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      initialDateRange: _startDate != null && _endDate != null 
          ? DateTimeRange(start: _startDate!, end: _endDate!)
          : null,
      locale: const Locale('fr', 'FR'),
      builder: (BuildContext context, Widget? child) {
        return Theme(
          data: ThemeData.light().copyWith(
            colorScheme: const ColorScheme.light(
              primary: Colors.green,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: Colors.black,
            ),
          ),
          child: child!,
        );
      },
    );
    
    if (picked != null) {
      setState(() {
        _startDate = picked.start;
        _endDate = picked.end;
      });
    }
  }

  Future<void> _submitPlant() async {
    if (_formKey.currentState!.validate()) {
      try {
        final plant = await _plantService.createPlant(
          nom: _nomController.text,
          espece: _especeController.text,
          imageFile: _imageFile,
          webImage: _webImage,
          originalFileName: _originalFileName,
        );
        setState(() {
          _createdPlantId = plant.id;
          _isFirstStep = false;
        });
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur lors de la création de la plante: $e')),
        );
      }
    }
  }

  Future<void> _submitCare() async {
    if (_formKey.currentState!.validate() && _createdPlantId != null && _startDate != null && _endDate != null) {
      try {
        final care = await _plantCareService.createPlantCare(
          plantId: _createdPlantId!,
          startDate: _startDate!,
          endDate: _endDate!,
          localisation: _localisationController.text,
          careInstructions: _careInstructionsController.text,
        );
        
        // Message de succès
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Garde créée avec succès !'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );
        
        // Navigation vers les détails de la garde
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => PlantCareDetailsScreen(
              careId: care['id'],
              isCurrentPlant: true,
            ),
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur lors de la création de la garde: $e')),
        );
      }
    }
  }

  Widget _getImageWidget() {
    if (kIsWeb && _webImage != null) {
      return Container(
        height: 200,
        width: double.infinity,
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8.0),
          child: Image.memory(
            _webImage!,
            fit: BoxFit.cover,
          ),
        ),
      );
    } else if (!kIsWeb && _imageFile != null) {
      return Container(
        height: 200,
        width: double.infinity,
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8.0),
          child: Image.file(
            _imageFile as File,
            fit: BoxFit.cover,
          ),
        ),
      );
    } else {
      return Container(
        height: 200,
        width: double.infinity,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(8.0),
          border: Border.all(color: Colors.grey[300]!, width: 2, style: BorderStyle.solid),
        ),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.add_photo_alternate, size: 50, color: Colors.grey),
              SizedBox(height: 8),
              Text('Ajouter une photo', style: TextStyle(color: Colors.grey)),
            ],
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isFirstStep ? 'Ajouter une plante' : 'Demander une garde'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: _isFirstStep ? _buildPlantForm() : _buildCareForm(),
        ),
      ),
    );
  }

  Widget _buildPlantForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _getImageWidget(),
        const SizedBox(height: 8),
        // Sur Flutter Web, afficher un sélecteur unique car la caméra n'est pas supportée
        kIsWeb 
          ? Center(
              child: ElevatedButton.icon(
                onPressed: () => _pickImage(ImageSource.gallery),
                icon: const Icon(Icons.photo_library),
                label: const Text('Sélectionner une image'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
              ),
            )
          : Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: () => _pickImage(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Photo'),
                ),
                ElevatedButton.icon(
                  onPressed: () => _pickImage(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Galerie'),
                ),
              ],
            ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _nomController,
          decoration: InputDecoration(
            labelText: 'Nom de la plante',
            filled: true,
            fillColor: Colors.green.withOpacity(0.1),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Colors.green),
            ),
          ),
          validator: (value) => value?.isEmpty ?? true ? 'Champ requis' : null,
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _especeController,
          decoration: InputDecoration(
            labelText: 'Espèce',
            filled: true,
            fillColor: Colors.green.withOpacity(0.1),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Colors.green),
            ),
          ),
          validator: (value) => value?.isEmpty ?? true ? 'Champ requis' : null,
        ),
        const SizedBox(height: 24),
        ElevatedButton(
          onPressed: _submitPlant,
          child: const Text('Suivant'),
        ),
      ],
    );
  }

  Widget _buildCareForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Période de garde',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        _startDate != null && _endDate != null
                            ? 'Du ${_dateFormat.format(_startDate!)} au ${_dateFormat.format(_endDate!)}'
                            : 'Sélectionnez une période',
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.date_range, color: Colors.green),
                      onPressed: () => _selectDateRange(context),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        AddressAutocompleteField(
          onAddressSelected: (address, lat, lng) {
            setState(() {
              _localisationController.text = address;
            });
            // Les coordonnées seront automatiquement géocodées côté serveur
            // mais on pourrait les stocker ici pour une utilisation future
          },
          initialValue: _localisationController.text,
          labelText: 'Localisation',
          hintText: 'Entrez l\'adresse de votre plante',
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.green.withOpacity(0.1),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Colors.green),
            ),
            prefixIcon: Icon(Icons.location_on, color: Colors.green[700]),
          ),
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _careInstructionsController,
          decoration: InputDecoration(
            labelText: 'Instructions de soin',
            filled: true,
            fillColor: Colors.green.withOpacity(0.1),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Colors.green),
            ),
          ),
          maxLines: 3,
        ),
        const SizedBox(height: 24),
        ElevatedButton(
          onPressed: _submitCare,
          child: const Text('Créer la demande de garde'),
        ),
      ],
    );
  }
}
