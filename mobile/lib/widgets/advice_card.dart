import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/advice.dart';
import '../views/create_advice_screen.dart';
import '../views/advice_details_screen.dart';
import '../views/validate_advice_screen.dart';
import 'image_zoom_dialog.dart';

class AdviceCard extends StatelessWidget {
  final PlantCareWithAdvice plantCare;
  final bool showAdviceDetails;
  final bool showEditButton;
  final int? currentBotanistId;
  final VoidCallback? onAdviceGiven;
  final VoidCallback? onValidation;

  const AdviceCard({
    Key? key,
    required this.plantCare,
    this.showAdviceDetails = false,
    this.showEditButton = false,
    this.currentBotanistId,
    this.onAdviceGiven,
    this.onValidation,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final hasAdvice = plantCare.currentAdvice != null;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _onCardTap(context),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header avec priorité et statut
              Row(
                children: [
                  // Icône de priorité
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getPriorityColor().withOpacity(0.1),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: _getPriorityColor().withOpacity(0.3)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          plantCare.priority.emoji,
                          style: const TextStyle(fontSize: 12),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          plantCare.priority.displayName,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: _getPriorityColor(),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const Spacer(),
                  
                  // Badge de statut
                  if (hasAdvice) _buildStatusBadge(),
                  if (plantCare.needsValidation) _buildValidationBadge(),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Informations sur la plante
              Row(
                children: [
                  GestureDetector(
                    onTap: plantCare.plantImageUrl != null 
                      ? () => ImageZoomDialog.show(
                          context, 
                          'http://localhost:8000/${plantCare.plantImageUrl!}',
                          title: plantCare.plantName,
                        )
                      : null,
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: plantCare.plantImageUrl != null 
                          ? Image.network(
                              'http://localhost:8000/${plantCare.plantImageUrl!}',
                              width: 40,
                              height: 40,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return Icon(
                                  Icons.eco,
                                  color: Colors.green.shade600,
                                  size: 24,
                                );
                              },
                            )
                          : Icon(
                              Icons.eco,
                              color: Colors.green.shade600,
                              size: 24,
                            ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          plantCare.plantName,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                        if (plantCare.plantSpecies != null) ...[
                          const SizedBox(height: 2),
                          Text(
                            plantCare.plantSpecies!,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade600,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ],
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(
                              Icons.person_outline,
                              size: 16,
                              color: Colors.grey.shade600,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              plantCare.ownerName,
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey.shade600,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Dates et localisation
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.calendar_today_outlined,
                          size: 16,
                          color: Colors.grey.shade600,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Garde: ${_formatDate(plantCare.startDate)} - ${_formatDate(plantCare.endDate)}',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade700,
                          ),
                        ),
                      ],
                    ),
                    if (plantCare.localisation != null) ...[
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Icon(
                            Icons.location_on_outlined,
                            size: 16,
                            color: Colors.grey.shade600,
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              plantCare.localisation!,
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey.shade700,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              
              // Conseil actuel (si existe)
              if (hasAdvice && showAdviceDetails) ...[
                const SizedBox(height: 12),
                _buildAdvicePreview(context, plantCare.currentAdvice!),
              ],
              
              // Instructions de garde
              if (plantCare.careInstructions != null && plantCare.careInstructions!.isNotEmpty) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        color: Colors.blue.shade700,
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          plantCare.careInstructions!,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.blue.shade800,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              
              const SizedBox(height: 16),
              
              // Actions
              Row(
                children: [
                  if (!hasAdvice) ...[
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _createAdvice(context),
                        icon: const Icon(Icons.add_comment, size: 18),
                        label: const Text('Donner un avis'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                  ] else ...[
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _viewAdviceDetails(context),
                        icon: const Icon(Icons.visibility, size: 18),
                        label: const Text('Voir détails'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                    
                    // Logique conditionnelle pour les boutons dans l'onglet "Avis"
                    if (showEditButton && plantCare.currentAdvice != null) ...[
                      const SizedBox(width: 8),
                      // Si c'est MON avis : bouton orange "Modifier l'avis"
                      if (currentBotanistId != null && 
                          plantCare.currentAdvice!.botanistId == currentBotanistId) ...[
                        ElevatedButton.icon(
                          onPressed: () => _editAdvice(context),
                          icon: const Icon(Icons.edit, size: 18),
                          label: const Text('Modifier l\'avis'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.orange,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ]
                      // Si c'est l'avis d'UN AUTRE botaniste : bouton bleu "Valider"
                      else if (currentBotanistId != null && 
                               plantCare.currentAdvice!.botanistId != currentBotanistId &&
                               plantCare.currentAdvice!.validationStatus == ValidationStatus.pending) ...[
                        ElevatedButton.icon(
                          onPressed: () => _validateAdvice(context),
                          icon: const Icon(Icons.verified_user, size: 18),
                          label: const Text('Valider'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge() {
    final advice = plantCare.currentAdvice!;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getValidationColor(advice.validationStatus).withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: _getValidationColor(advice.validationStatus).withOpacity(0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            advice.validationStatus.emoji,
            style: const TextStyle(fontSize: 12),
          ),
          const SizedBox(width: 4),
          Text(
            advice.validationStatus.displayName,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: _getValidationColor(advice.validationStatus),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildValidationBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.orange.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('⚠️', style: TextStyle(fontSize: 12)),
          const SizedBox(width: 4),
          Text(
            'À valider',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.orange.shade700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAdvicePreview(BuildContext context, Advice advice) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.psychology,
                color: Colors.green.shade700,
                size: 18,
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  advice.title,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.green.shade800,
                  ),
                ),
              ),
              if (advice.botanist != null) ...[
                Text(
                  'v${advice.version}',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 6),
          Text(
            advice.content,
            style: TextStyle(
              fontSize: 13,
              color: Colors.green.shade700,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          if (advice.botanist != null) ...[
            const SizedBox(height: 6),
            Text(
              'Par ${advice.botanist!.fullName}',
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getPriorityColor() {
    switch (plantCare.priority) {
      case AdvicePriority.urgent:
        return Colors.red;
      case AdvicePriority.followUp:
        return Colors.orange;
      case AdvicePriority.normal:
        return Colors.green;
    }
  }

  Color _getValidationColor(ValidationStatus status) {
    switch (status) {
      case ValidationStatus.validated:
        return Colors.green;
      case ValidationStatus.rejected:
        return Colors.red;
      case ValidationStatus.needsRevision:
        return Colors.orange;
      case ValidationStatus.pending:
        return Colors.grey;
    }
  }

  String _formatDate(DateTime date) {
    return DateFormat('dd/MM/yyyy').format(date);
  }

  void _onCardTap(BuildContext context) {
    if (plantCare.currentAdvice != null) {
      _viewAdviceDetails(context);
    } else {
      _createAdvice(context);
    }
  }

  void _createAdvice(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CreateAdviceScreen(
          plantCare: plantCare,
          onAdviceCreated: onAdviceGiven,
        ),
      ),
    );
  }

  void _viewAdviceDetails(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AdviceDetailsScreen(
          plantCare: plantCare,
          onAdviceUpdated: onAdviceGiven,
        ),
      ),
    );
  }

  void _editAdvice(BuildContext context) {
    if (plantCare.currentAdvice != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => CreateAdviceScreen(
            plantCare: plantCare,
            existingAdvice: plantCare.currentAdvice!,
            isEditing: true,
            onAdviceCreated: onAdviceGiven,
          ),
        ),
      );
    }
  }

  void _validateAdvice(BuildContext context) {
    if (plantCare.currentAdvice != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ValidateAdviceScreen(
            advice: plantCare.currentAdvice!,
            plantCare: plantCare,
            onValidated: onValidation,
          ),
        ),
      );
    }
  }
}
