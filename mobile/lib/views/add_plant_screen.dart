import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile/services/plant_service.dart';
import 'package:mobile/services/plant_care_service.dart';
import 'package:intl/intl.dart';

class AddPlantScreen extends StatefulWidget {
  const AddPlantScreen({Key? key}) : super(key: key);

  @override
  State<AddPlantScreen> createState() => _AddPlantScreenState();
}

class _AddPlantScreenState extends State<AddPlantScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isFirstStep = true;
  File? _imageFile;
  late PlantService _plantService;
  late PlantCareService _plantCareService;
  int? _createdPlantId;

  // Contrôleurs pour les champs de la plante
  final _nomController = TextEditingController();
  final _especeController = TextEditingController();
  final _descriptionController = TextEditingController();

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
    _descriptionController.dispose();
    _localisationController.dispose();
    _careInstructionsController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final pickedFile = await ImagePicker().pickImage(source: source);
    if (pickedFile != null) {
      setState(() {
        _imageFile = File(pickedFile.path);
      });
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
          description: _descriptionController.text,
          imageFile: _imageFile,
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
        await _plantCareService.createPlantCare(
          plantId: _createdPlantId!,
          startDate: _startDate!,
          endDate: _endDate!,
          localisation: _localisationController.text,
          careInstructions: _careInstructionsController.text,
        );
        Navigator.pop(context);
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur lors de la création de la garde: $e')),
        );
      }
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
        if (_imageFile != null)
          Image.file(
            _imageFile!,
            height: 200,
            fit: BoxFit.cover,
          ),
        Row(
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
        const SizedBox(height: 16),
        TextFormField(
          controller: _descriptionController,
          decoration: InputDecoration(
            labelText: 'Description',
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
        TextFormField(
          controller: _localisationController,
          decoration: InputDecoration(
            labelText: 'Localisation',
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
