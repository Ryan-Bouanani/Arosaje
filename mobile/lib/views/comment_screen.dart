import 'package:flutter/material.dart';
import 'base_page_botaniste.dart';
import 'plant_detail_botaniste.dart';
import 'package:mobile/services/advice_service.dart';

class CommentScreen extends StatefulWidget {
  const CommentScreen({super.key});

  @override
  State<CommentScreen> createState() => _CommentScreenState();
}

class _CommentScreenState extends State<CommentScreen> {
  late final AdviceService _adviceService;
  bool _isInitialized = false;
  bool _isLoading = true;
  String? _error;
  
  List<Map<String, dynamic>> pendingRequests = [];
  List<Map<String, dynamic>> myAdvices = [];

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  Future<void> _initializeService() async {
    try {
      _adviceService = await AdviceService.init();
      setState(() {
        _isInitialized = true;
      });
      await _loadData();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadData() async {
    if (!_isInitialized) return;
    
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final requests = await _adviceService.getPendingAdviceRequests();
      final advices = await _adviceService.getMyAdvices();
      
      if (mounted) {
        setState(() {
          pendingRequests = requests;
          myAdvices = advices;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _deleteAdvice(int adviceId) async {
    try {
      await _adviceService.deleteAdvice(adviceId);
      await _loadData(); // Recharger les données après la suppression
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur lors de la suppression: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return BasePageBotaniste(
      body: _isLoading
        ? const Center(child: CircularProgressIndicator())
        : _error != null
          ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
          : RefreshIndicator(
              onRefresh: _loadData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Liste commentaires',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1B4332),
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Section "demande de commentaire"
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Demande de commentaire',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 16),
                            if (pendingRequests.isEmpty)
                              const Center(
                                child: Text('Aucune demande de conseil en attente'),
                              )
                            else
                              ...pendingRequests.map((request) => Container(
                                margin: const EdgeInsets.only(bottom: 12),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(8),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.grey.withOpacity(0.2),
                                      spreadRadius: 1,
                                      blurRadius: 2,
                                      offset: const Offset(0, 1),
                                    ),
                                  ],
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Plante : ${(request['plant'] as Map<String, dynamic>?)?.containsKey('nom') ?? false ? request['plant']['nom'] : 'Non spécifié'}',
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.black87,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      'Espèce : ${(request['plant'] as Map<String, dynamic>?)?.containsKey('espece') ?? false ? request['plant']['espece'] : 'Non spécifiée'}',
                                      style: const TextStyle(
                                        fontSize: 14,
                                        color: Colors.black54,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    ElevatedButton(
                                      onPressed: () {
                                        if (request['plant'] != null && request['plant']['id'] != null) {
                                          Navigator.push(
                                            context,
                                            MaterialPageRoute(
                                              builder: (context) => PlantDetailBotaniste(
                                                plantId: request['plant']['id'],
                                              ),
                                            ),
                                          );
                                        }
                                      },
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: const Color(0xFF1B4332),
                                        foregroundColor: Colors.white,
                                      ),
                                      child: const Text('Donner un conseil'),
                                    ),
                                  ],
                                ),
                              )),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Section "vos commentaires"
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Vos commentaires',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 16),
                            if (myAdvices.isEmpty)
                              const Center(
                                child: Text('Vous n\'avez pas encore donné de conseil'),
                              )
                            else
                              ...myAdvices.map((advice) => Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: GestureDetector(
                                  onTap: () {
                                    if (advice['plant_id'] != null) {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => PlantDetailBotaniste(
                                            plantId: advice['plant_id'],
                                          ),
                                        ),
                                      );
                                    }
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(8),
                                      boxShadow: [
                                        BoxShadow(
                                          color: Colors.grey.withOpacity(0.2),
                                          spreadRadius: 1,
                                          blurRadius: 2,
                                          offset: const Offset(0, 1),
                                        ),
                                      ],
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Expanded(
                                              child: Text(
                                                advice['texte'] ?? 'Pas de texte',
                                                style: const TextStyle(
                                                  fontSize: 14,
                                                  color: Colors.black87,
                                                ),
                                              ),
                                            ),
                                            IconButton(
                                              icon: const Icon(Icons.delete, color: Colors.red),
                                              onPressed: () {
                                                if (advice['id'] != null) {
                                                  _deleteAdvice(advice['id']);
                                                }
                                              },
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          'Status: ${advice['status'] ?? 'Non spécifié'}',
                                          style: const TextStyle(
                                            fontSize: 12,
                                            color: Colors.grey,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              )).toList(),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
      currentIndex: 1,
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return Colors.orange;
      case 'validated':
        return Colors.green;
      case 'rejected':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'pending':
        return 'En attente';
      case 'validated':
        return 'Validé';
      case 'rejected':
        return 'Rejeté';
      default:
        return 'Statut inconnu';
    }
  }
}
