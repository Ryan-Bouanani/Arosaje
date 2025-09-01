import 'package:flutter/material.dart';
import 'package:mobile/services/care_report_service.dart';

class CareReportsBotanistScreen extends StatefulWidget {
  const CareReportsBotanistScreen({super.key});

  @override
  State<CareReportsBotanistScreen> createState() => _CareReportsBotanistScreenState();
}

class _CareReportsBotanistScreenState extends State<CareReportsBotanistScreen> {
  late final CareReportService _careReportService;
  List<Map<String, dynamic>> _reports = [];
  bool _isLoading = true;
  bool _isInitialized = false;
  String? _error;

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
      await _loadReports();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadReports() async {
    if (!_isInitialized) return;
    
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final reports = await _careReportService.getCareReportsForBotanist();
      
      setState(() {
        _reports = reports;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Color _getHealthColor(String level) {
    switch (level.toLowerCase()) {
      case 'bon':
        return Colors.green;
      case 'moyen':
        return Colors.orange;
      case 'bas':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Widget _buildHealthChip(String label, String value) {
    return Chip(
      label: Text(
        '$label: $value',
        style: const TextStyle(fontSize: 12),
      ),
      backgroundColor: _getHealthColor(value).withOpacity(0.2),
      side: BorderSide(color: _getHealthColor(value)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Rapports de Séances'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
        ? const Center(child: CircularProgressIndicator())
        : _error != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    _error!,
                    style: const TextStyle(color: Colors.red),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadReports,
                    child: const Text('Réessayer'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: _loadReports,
              child: _reports.isEmpty
                ? const Center(
                    child: Text(
                      'Aucun rapport de séance disponible',
                      style: TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _reports.length,
                    itemBuilder: (context, index) {
                      final report = _reports[index];
                      final sessionDate = DateTime.parse(report['session_date']);
                      
                      return Card(
                        margin: const EdgeInsets.only(bottom: 16),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // En-tête avec informations de base
                              Row(
                                children: [
                                  const Icon(Icons.local_florist, color: Colors.green),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          report['plant_name'] ?? 'Plante inconnue',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 16,
                                          ),
                                        ),
                                        Text(
                                          'Propriétaire: ${report['owner_name'] ?? 'Inconnu'}',
                                          style: const TextStyle(
                                            color: Colors.grey,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      Text(
                                        '${sessionDate.day}/${sessionDate.month}/${sessionDate.year}',
                                        style: const TextStyle(fontWeight: FontWeight.w500),
                                      ),
                                      Text(
                                        '${sessionDate.hour}:${sessionDate.minute.toString().padLeft(2, '0')}',
                                        style: const TextStyle(color: Colors.grey, fontSize: 12),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              
                              const SizedBox(height: 12),
                              
                              // Gardien
                              Text(
                                'Gardien: ${report['caretaker_name'] ?? 'Inconnu'}',
                                style: const TextStyle(fontWeight: FontWeight.w500),
                              ),
                              
                              const SizedBox(height: 12),
                              
                              // Évaluations de santé
                              Wrap(
                                spacing: 8,
                                runSpacing: 4,
                                children: [
                                  _buildHealthChip('Santé', report['health_level'] ?? ''),
                                  _buildHealthChip('Hydratation', report['hydration_level'] ?? ''),
                                  _buildHealthChip('Vitalité', report['vitality_level'] ?? ''),
                                ],
                              ),
                              
                              const SizedBox(height: 12),
                              
                              // Description
                              if (report['description'] != null && report['description'].toString().isNotEmpty)
                                Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: Colors.grey[100],
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'Observations:',
                                        style: TextStyle(fontWeight: FontWeight.w500),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(report['description']),
                                    ],
                                  ),
                                ),
                              
                              // Photo si disponible
                              if (report['photo_url'] != null)
                                Container(
                                  margin: const EdgeInsets.only(top: 12),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: Colors.blue[50],
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: const Row(
                                    children: [
                                      Icon(Icons.photo, color: Colors.blue, size: 20),
                                      SizedBox(width: 8),
                                      Text('Photo jointe', style: TextStyle(color: Colors.blue)),
                                    ],
                                  ),
                                ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
            ),
    );
  }
}