import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/plant_care_advice.dart';

class AdviceDetailsScreen extends StatelessWidget {
  final PlantCareWithAdvice plantCare;
  final VoidCallback? onAdviceUpdated;

  const AdviceDetailsScreen({
    Key? key,
    required this.plantCare,
    this.onAdviceUpdated,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final advice = plantCare.currentAdvice!;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Détails du conseil'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          if (plantCare.adviceHistory.length > 1)
            IconButton(
              onPressed: () => _showVersionHistory(context),
              icon: const Icon(Icons.history),
              tooltip: 'Historique des versions',
            ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header avec infos de la plante
            Container(
              color: Colors.green.shade50,
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.shade100,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.eco,
                      color: Colors.green.shade700,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          plantCare.plantName,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (plantCare.plantSpecies != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            plantCare.plantSpecies!,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade600,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ],
                        const SizedBox(height: 6),
                        Text(
                          'Propriétaire: ${plantCare.ownerName}',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Statut et priorité
                  Row(
                    children: [
                      _buildPriorityChip(advice.priority),
                      const SizedBox(width: 8),
                      _buildStatusChip(advice.validationStatus),
                    ],
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Titre du conseil
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(12),
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
                              size: 24,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                advice.title,
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green.shade800,
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8, 
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade200,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                'v${advice.version}',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade700,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Contenu du conseil
                  Text(
                    'Conseil détaillé',
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
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Text(
                      advice.content,
                      style: const TextStyle(
                        fontSize: 15,
                        height: 1.5,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Informations sur l'auteur
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
                              Icons.account_circle,
                              color: Colors.blue.shade700,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Botaniste expert',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: Colors.blue.shade800,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        if (advice.botanist != null) ...[
                          Text(
                            advice.botanist!.fullName,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.blue.shade700,
                            ),
                          ),
                        ],
                        const SizedBox(height: 4),
                        Text(
                          'Publié le ${DateFormat('dd/MM/yyyy à HH:mm').format(advice.createdAt)}',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                        ),
                        if (advice.updatedAt != advice.createdAt) ...[
                          const SizedBox(height: 2),
                          Text(
                            'Mis à jour le ${DateFormat('dd/MM/yyyy à HH:mm').format(advice.updatedAt)}',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade600,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  
                  // Validation
                  if (advice.validationStatus != ValidationStatus.pending) ...[
                    const SizedBox(height: 16),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: _getValidationBackgroundColor(advice.validationStatus),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _getValidationBorderColor(advice.validationStatus),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                advice.validationStatus.emoji,
                                style: const TextStyle(fontSize: 20),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Validation: ${advice.validationStatus.displayName}',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: _getValidationTextColor(advice.validationStatus),
                                ),
                              ),
                            ],
                          ),
                          if (advice.validator != null) ...[
                            const SizedBox(height: 8),
                            Text(
                              'Par ${advice.validator!.fullName}',
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey.shade700,
                              ),
                            ),
                          ],
                          if (advice.validatedAt != null) ...[
                            const SizedBox(height: 4),
                            Text(
                              'Le ${DateFormat('dd/MM/yyyy à HH:mm').format(advice.validatedAt!)}',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade600,
                              ),
                            ),
                          ],
                          if (advice.validationComment != null) ...[
                            const SizedBox(height: 12),
                            Text(
                              'Commentaire:',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Colors.grey.shade800,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              advice.validationComment!,
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey.shade700,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                  
                  // Instructions de garde (référence)
                  if (plantCare.careInstructions != null && 
                      plantCare.careInstructions!.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    Text(
                      'Instructions du propriétaire',
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
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.orange.shade200),
                      ),
                      child: Text(
                        plantCare.careInstructions!,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.orange.shade800,
                        ),
                      ),
                    ),
                  ],
                  
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPriorityChip(AdvicePriority priority) {
    Color color = _getPriorityColor(priority);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(priority.emoji, style: const TextStyle(fontSize: 14)),
          const SizedBox(width: 6),
          Text(
            priority.displayName,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChip(ValidationStatus status) {
    Color color = _getValidationColor(status);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(status.emoji, style: const TextStyle(fontSize: 14)),
          const SizedBox(width: 6),
          Text(
            status.displayName,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
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

  Color _getValidationBackgroundColor(ValidationStatus status) {
    switch (status) {
      case ValidationStatus.validated:
        return Colors.green.shade50;
      case ValidationStatus.rejected:
        return Colors.red.shade50;
      case ValidationStatus.needsRevision:
        return Colors.orange.shade50;
      case ValidationStatus.pending:
        return Colors.grey.shade50;
    }
  }

  Color _getValidationBorderColor(ValidationStatus status) {
    switch (status) {
      case ValidationStatus.validated:
        return Colors.green.shade200;
      case ValidationStatus.rejected:
        return Colors.red.shade200;
      case ValidationStatus.needsRevision:
        return Colors.orange.shade200;
      case ValidationStatus.pending:
        return Colors.grey.shade200;
    }
  }

  Color _getValidationTextColor(ValidationStatus status) {
    switch (status) {
      case ValidationStatus.validated:
        return Colors.green.shade800;
      case ValidationStatus.rejected:
        return Colors.red.shade800;
      case ValidationStatus.needsRevision:
        return Colors.orange.shade800;
      case ValidationStatus.pending:
        return Colors.grey.shade800;
    }
  }

  void _showVersionHistory(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.9,
        minChildSize: 0.5,
        expand: false,
        builder: (context, scrollController) => Column(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Historique des versions',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey.shade800,
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView.builder(
                controller: scrollController,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: plantCare.adviceHistory.length,
                itemBuilder: (context, index) {
                  final historyAdvice = plantCare.adviceHistory[index];
                  final isCurrent = historyAdvice.isCurrentVersion;
                  
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isCurrent ? Colors.green.shade50 : Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isCurrent ? Colors.green.shade200 : Colors.grey.shade300,
                        width: isCurrent ? 2 : 1,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8, 
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: isCurrent ? Colors.green : Colors.grey,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                'v${historyAdvice.version}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            if (isCurrent) ...[
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.green.shade100,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  'Actuelle',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.green.shade700,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                            const Spacer(),
                            _buildPriorityChip(historyAdvice.priority),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          historyAdvice.title,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.grey.shade800,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          historyAdvice.content,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade700,
                          ),
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${DateFormat('dd/MM/yyyy à HH:mm').format(historyAdvice.createdAt)} par ${historyAdvice.botanist?.fullName ?? 'Inconnu'}',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}