import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/advice.dart';
import '../providers/advice_provider.dart';

class CreateAdviceScreen extends StatefulWidget {
  final PlantCareWithAdvice plantCare;
  final Advice? existingAdvice;
  final bool isEditing;
  final VoidCallback? onAdviceCreated;

  const CreateAdviceScreen({
    Key? key,
    required this.plantCare,
    this.existingAdvice,
    this.isEditing = false,
    this.onAdviceCreated,
  }) : super(key: key);

  @override
  State<CreateAdviceScreen> createState() => _CreateAdviceScreenState();
}

class _CreateAdviceScreenState extends State<CreateAdviceScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  
  AdvicePriority _selectedPriority = AdvicePriority.normal;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    
    // Pré-remplir les champs si on modifie un avis existant
    if (widget.isEditing && widget.existingAdvice != null) {
      _titleController.text = widget.existingAdvice!.title;
      _contentController.text = widget.existingAdvice!.content;
      _selectedPriority = widget.existingAdvice!.priority;
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _contentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isEditing ? 'Modifier l\'avis botanique' : 'Donner un avis botanique'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Header avec infos de la plante
          Container(
            color: Colors.green.shade50,
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: Colors.green.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: widget.plantCare.plantImageUrl != null 
                        ? Image.network(
                            'http://localhost:8000/${widget.plantCare.plantImageUrl!}',
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Icon(
                                Icons.eco,
                                color: Colors.green.shade700,
                                size: 32,
                              );
                            },
                          )
                        : Icon(
                            Icons.eco,
                            color: Colors.green.shade700,
                            size: 32,
                          ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.plantCare.plantName,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      if (widget.plantCare.plantSpecies != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          widget.plantCare.plantSpecies!,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade600,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ],
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Icon(
                            Icons.person_outline,
                            size: 16,
                            color: Colors.grey.shade600,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'Propriétaire: ${widget.plantCare.ownerName}',
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey.shade700,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Formulaire
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Instructions de garde si présentes
                    if (widget.plantCare.careInstructions != null && 
                        widget.plantCare.careInstructions!.isNotEmpty) ...[
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.blue.shade200),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  Icons.info_outline,
                                  color: Colors.blue.shade700,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Instructions du propriétaire',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.blue.shade800,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              widget.plantCare.careInstructions!,
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.blue.shade700,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                    
                    // Titre du conseil
                    Text(
                      'Titre de votre conseil',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _titleController,
                      decoration: InputDecoration(
                        hintText: 'Ex: Arrosage optimal, Exposition à la lumière...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.grey.shade50,
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Veuillez saisir un titre';
                        }
                        if (value.trim().length < 5) {
                          return 'Le titre doit contenir au moins 5 caractères';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Priorité
                    Text(
                      'Priorité du conseil',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        children: AdvicePriority.values.map((priority) {
                          return RadioListTile<AdvicePriority>(
                            title: Row(
                              children: [
                                Text(priority.emoji, style: const TextStyle(fontSize: 16)),
                                const SizedBox(width: 8),
                                Text(priority.displayName),
                              ],
                            ),
                            subtitle: Text(
                              _getPriorityDescription(priority),
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade600,
                              ),
                            ),
                            value: priority,
                            groupValue: _selectedPriority,
                            onChanged: (value) {
                              setState(() {
                                _selectedPriority = value!;
                              });
                            },
                            activeColor: _getPriorityColor(priority),
                          );
                        }).toList(),
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Contenu du conseil
                    Text(
                      'Votre conseil détaillé',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _contentController,
                      maxLines: 8,
                      decoration: InputDecoration(
                        hintText: 'Décrivez votre conseil en détail...\n\n'
                            '• Diagnostic\n'
                            '• Recommandations\n'
                            '• Actions à entreprendre\n'
                            '• Signes à surveiller...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.grey.shade50,
                        alignLabelWithHint: true,
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Veuillez saisir le contenu du conseil';
                        }
                        if (value.trim().length < 20) {
                          return 'Le conseil doit être plus détaillé (min. 20 caractères)';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ),
          
          // Boutons d'action
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.2),
                  spreadRadius: 1,
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _isSubmitting ? null : () => Navigator.pop(context),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('Annuler'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: _isSubmitting ? null : _submitAdvice,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: _isSubmitting
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2,
                              ),
                            )
                          : Text(
                              widget.isEditing ? 'Modifier le conseil' : 'Publier le conseil',
                              style: const TextStyle(fontWeight: FontWeight.w600),
                            ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getPriorityDescription(AdvicePriority priority) {
    switch (priority) {
      case AdvicePriority.urgent:
        return 'Action immédiate requise pour sauver la plante';
      case AdvicePriority.followUp:
        return 'Surveillance et suivi nécessaires';
      case AdvicePriority.normal:
        return 'Conseil préventif et d\'entretien général';
    }
  }

  Color _getPriorityColor(AdvicePriority priority) {
    switch (priority) {
      case AdvicePriority.urgent:
        return Colors.red;
      case AdvicePriority.followUp:
        return Colors.orange;
      case AdvicePriority.normal:
        return Colors.green;
    }
  }

  Future<void> _submitAdvice() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Vérification de sécurité pour plantCareId
    if (widget.plantCare.id == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.error, color: Colors.white),
              const SizedBox(width: 8),
              const Expanded(
                child: Text('Erreur: Identifiant de garde manquant'),
              ),
            ],
          ),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    final provider = Provider.of<AdviceProvider>(context, listen: false);
    
    // Pour l'édition et la création, on utilise la même méthode createAdvice 
    // car l'API backend gère automatiquement la création de nouvelles versions
    final advice = await provider.createAdvice(
      plantCareId: widget.plantCare.id!,
      title: _titleController.text.trim(),
      content: _contentController.text.trim(),
      priority: _selectedPriority,
    );

    setState(() {
      _isSubmitting = false;
    });

    if (advice != null) {
      // Succès
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  widget.isEditing 
                    ? 'Conseil modifié avec succès ! Une nouvelle version a été créée.'
                    : 'Conseil publié avec succès ! ${_selectedPriority == AdvicePriority.urgent ? "Le propriétaire sera notifié immédiatement." : "Le propriétaire sera notifié."}',
                ),
              ),
            ],
          ),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 4),
        ),
      );

      widget.onAdviceCreated?.call();
      Navigator.pop(context);
    } else {
      // Erreur
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.error, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  provider.error ?? 'Erreur lors de la publication du conseil',
                ),
              ),
            ],
          ),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }
}
