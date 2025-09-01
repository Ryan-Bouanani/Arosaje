import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../models/plant_care_advice.dart';
import '../providers/plant_care_advice_provider.dart';

class ValidateAdviceScreen extends StatefulWidget {
  final PlantCareAdvice advice;
  final PlantCareWithAdvice plantCare;
  final VoidCallback? onValidated;

  const ValidateAdviceScreen({
    Key? key,
    required this.advice,
    required this.plantCare,
    this.onValidated,
  }) : super(key: key);

  @override
  State<ValidateAdviceScreen> createState() => _ValidateAdviceScreenState();
}

class _ValidateAdviceScreenState extends State<ValidateAdviceScreen> {
  final _commentController = TextEditingController();
  ValidationStatus? _selectedStatus;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Validation du conseil'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Header avec infos du conseil
          Container(
            color: Colors.blue.shade50,
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade100,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.psychology,
                        color: Colors.blue.shade700,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.advice.title,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Par ${widget.advice.botanist?.fullName ?? "Botaniste"}',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Publié le ${DateFormat('dd/MM/yyyy à HH:mm').format(widget.advice.createdAt)}',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  'Plante: ${widget.plantCare.plantName}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade700,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Contenu du conseil
                  Text(
                    'Conseil à valider',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey.shade800,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Text(
                      widget.advice.content,
                      style: const TextStyle(
                        fontSize: 15,
                        height: 1.5,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Choix de validation
                  Text(
                    'Votre évaluation',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey.shade800,
                    ),
                  ),
                  const SizedBox(height: 12),
                  
                  Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Column(
                      children: [
                        _buildValidationOption(
                          ValidationStatus.validated,
                          'Valider ce conseil',
                          'Le conseil est pertinent et de qualité',
                          Colors.green,
                          Icons.check_circle,
                        ),
                        const Divider(height: 1),
                        _buildValidationOption(
                          ValidationStatus.needsRevision,
                          'Demander une révision',
                          'Le conseil nécessite des améliorations',
                          Colors.orange,
                          Icons.edit,
                        ),
                        const Divider(height: 1),
                        _buildValidationOption(
                          ValidationStatus.rejected,
                          'Rejeter ce conseil',
                          'Le conseil n\'est pas approprié',
                          Colors.red,
                          Icons.cancel,
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Commentaire
                  Text(
                    'Commentaire ${_selectedStatus == ValidationStatus.validated ? "(optionnel)" : "(requis)"}',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey.shade800,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _commentController,
                    maxLines: 4,
                    decoration: InputDecoration(
                      hintText: _getCommentHint(),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      filled: true,
                      fillColor: Colors.grey.shade50,
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Informations sur la validation
                  Container(
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
                              'Système de validation par les pairs',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: Colors.blue.shade800,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Votre validation aide à maintenir la qualité des conseils botaniques. '
                          'Le botaniste auteur sera notifié de votre évaluation.',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.blue.shade700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
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
                      onPressed: _isSubmitting || _selectedStatus == null ? null : _submitValidation,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _selectedStatus != null ? _getStatusColor(_selectedStatus!) : Colors.grey,
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
                              _getActionButtonText(),
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

  Widget _buildValidationOption(
    ValidationStatus status,
    String title,
    String description,
    Color color,
    IconData icon,
  ) {
    final isSelected = _selectedStatus == status;
    
    return RadioListTile<ValidationStatus>(
      title: Row(
        children: [
          Icon(
            icon,
            color: isSelected ? color : Colors.grey.shade400,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              color: isSelected ? color : Colors.black87,
            ),
          ),
        ],
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(left: 28),
        child: Text(
          description,
          style: TextStyle(
            fontSize: 12,
            color: isSelected ? color.withOpacity(0.8) : Colors.grey.shade600,
          ),
        ),
      ),
      value: status,
      groupValue: _selectedStatus,
      onChanged: (value) {
        setState(() {
          _selectedStatus = value;
        });
      },
      activeColor: color,
      dense: false,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
    );
  }

  String _getCommentHint() {
    if (_selectedStatus == null) {
      return 'Expliquez votre évaluation...';
    }
    
    switch (_selectedStatus!) {
      case ValidationStatus.validated:
        return 'Optionnel: Pourquoi ce conseil vous semble-t-il de qualité?';
      case ValidationStatus.needsRevision:
        return 'Expliquez quels aspects nécessitent des améliorations...';
      case ValidationStatus.rejected:
        return 'Expliquez pourquoi ce conseil ne vous semble pas approprié...';
      default:
        return 'Expliquez votre évaluation...';
    }
  }

  String _getActionButtonText() {
    if (_selectedStatus == null) return 'Sélectionner une option';
    
    switch (_selectedStatus!) {
      case ValidationStatus.validated:
        return 'Valider le conseil';
      case ValidationStatus.needsRevision:
        return 'Demander une révision';
      case ValidationStatus.rejected:
        return 'Rejeter le conseil';
      default:
        return 'Soumettre';
    }
  }

  Color _getStatusColor(ValidationStatus status) {
    switch (status) {
      case ValidationStatus.validated:
        return Colors.green;
      case ValidationStatus.needsRevision:
        return Colors.orange;
      case ValidationStatus.rejected:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Future<void> _submitValidation() async {
    if (_selectedStatus == null) return;
    
    // Vérifier que le commentaire est requis pour certains status
    if ((_selectedStatus == ValidationStatus.rejected || _selectedStatus == ValidationStatus.needsRevision) &&
        _commentController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Un commentaire est requis pour ${_selectedStatus!.displayName.toLowerCase()}'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    final provider = Provider.of<PlantCareAdviceProvider>(context, listen: false);
    final result = await provider.validateAdvice(
      widget.advice.id,
      _selectedStatus!,
      _commentController.text.trim().isNotEmpty ? _commentController.text.trim() : null,
    );

    setState(() {
      _isSubmitting = false;
    });

    if (result != null) {
      // Succès
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(
                _selectedStatus == ValidationStatus.validated ? Icons.check_circle : Icons.info,
                color: Colors.white,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Validation enregistrée. ${_selectedStatus == ValidationStatus.validated ? "Le botaniste sera félicité !" : "Le botaniste sera notifié de vos suggestions."}',
                ),
              ),
            ],
          ),
          backgroundColor: _getStatusColor(_selectedStatus!),
          duration: const Duration(seconds: 4),
        ),
      );

      widget.onValidated?.call();
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
                  provider.error ?? 'Erreur lors de la validation',
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