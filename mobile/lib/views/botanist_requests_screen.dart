import 'package:flutter/material.dart';
import 'package:mobile/services/advice_service.dart';
import 'base_page_botaniste.dart';

class BotanistRequestsScreen extends StatefulWidget {
  const BotanistRequestsScreen({super.key});

  @override
  State<BotanistRequestsScreen> createState() => _BotanistRequestsScreenState();
}

class _BotanistRequestsScreenState extends State<BotanistRequestsScreen> {
  late final AdviceService _adviceService;
  List<Map<String, dynamic>> _pendingRequests = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    try {
      _adviceService = await AdviceService.init();
      await _loadPendingRequests();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadPendingRequests() async {
    try {
      final requests = await _adviceService.getPendingAdviceRequests();
      setState(() {
        _pendingRequests = requests;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return BasePageBotaniste(
      currentIndex: 2,
      body: Scaffold(
        appBar: AppBar(
          title: const Text('Demandes de Conseil'),
          backgroundColor: Colors.green,
          foregroundColor: Colors.white,
        ),
        body: _error != null
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(_error!, style: const TextStyle(color: Colors.red)),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loadPendingRequests,
                      child: const Text('Réessayer'),
                    ),
                  ],
                ),
              )
            : _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _pendingRequests.isEmpty
                    ? const Center(
                        child: Text('Aucune demande de conseil en attente.'),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _pendingRequests.length,
                        itemBuilder: (context, index) {
                          final request = _pendingRequests[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    request['plant']?['nom'] ?? 'Plante inconnue',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text('Espèce: ${request['plant']?['espece'] ?? 'Non spécifiée'}'),
                                  const SizedBox(height: 8),
                                  Text(request['texte'] ?? ''),
                                  const SizedBox(height: 12),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: [
                                      TextButton(
                                        onPressed: () {
                                          // TODO: Implémenter la validation/rejet
                                        },
                                        child: const Text('Rejeter'),
                                      ),
                                      const SizedBox(width: 8),
                                      ElevatedButton(
                                        onPressed: () {
                                          // TODO: Implémenter la validation/rejet
                                        },
                                        child: const Text('Valider'),
                                      ),
                                    ],
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