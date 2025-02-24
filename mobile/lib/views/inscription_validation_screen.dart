import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../models/user.dart';

class InscriptionValidationScreen extends StatefulWidget {
  const InscriptionValidationScreen({super.key});

  @override
  State<InscriptionValidationScreen> createState() =>
      _InscriptionValidationScreenState();
}

class _InscriptionValidationScreenState
    extends State<InscriptionValidationScreen> {
  late Future<AuthService> _authServiceFuture;
  List<User> _pendingAccounts = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _authServiceFuture = AuthService.getInstance();
    _loadPendingAccounts();
  }

  Future<void> _loadPendingAccounts() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });
      
      final authService = await _authServiceFuture;
      final accounts = await authService.getPendingAccounts();
      
      if (mounted) {
        setState(() {
          _pendingAccounts = accounts;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = "Erreur lors du chargement des comptes : $e";
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleValidation(User user, bool isApproved) async {
    try {
      final authService = await _authServiceFuture;
      
      if (isApproved) {
        await authService.verifyAccount(user.id);
      } else {
        await authService.rejectAccount(user.id);
      }

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isApproved
                ? 'Utilisateur validé avec succès'
                : 'Utilisateur refusé avec succès',
          ),
          backgroundColor: isApproved ? Colors.green : Colors.red,
        ),
      );

      await _loadPendingAccounts();
    } catch (e) {
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Erreur lors de l'action : $e"),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Validation des inscriptions',
          style: TextStyle(color: Colors.black),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          color: Colors.grey[100],
          border: Border.all(
            color: Colors.blue,
            width: 2,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              const Text(
                'Validation des inscriptions',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              if (_isLoading)
                const Expanded(
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (_error != null)
                Expanded(
                  child: Center(
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
                          onPressed: _loadPendingAccounts,
                          child: const Text("Réessayer"),
                        ),
                      ],
                    ),
                  ),
                )
              else if (_pendingAccounts.isEmpty)
                const Expanded(
                  child: Center(
                    child: Text(
                      "Aucun compte en attente de validation",
                      style: TextStyle(fontSize: 16),
                    ),
                  ),
                )
              else
                Expanded(
                  child: RefreshIndicator(
                    onRefresh: _loadPendingAccounts,
                    child: ListView.builder(
                      itemCount: _pendingAccounts.length,
                      itemBuilder: (context, index) {
                        final user = _pendingAccounts[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 16),
                          elevation: 2,
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        "${user.prenom} ${user.nom}",
                                        style: const TextStyle(
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      Text(user.email),
                                      if (user.telephone != null)
                                        Text("Tél : ${user.telephone}"),
                                      Text("Rôle : ${user.role}"),
                                    ],
                                  ),
                                ),
                                Row(
                                  children: [
                                    ElevatedButton(
                                      onPressed: () =>
                                          _handleValidation(user, true),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.green,
                                        padding: const EdgeInsets.all(12),
                                        minimumSize: const Size(50, 50),
                                      ),
                                      child: const Icon(Icons.check,
                                          color: Colors.white),
                                    ),
                                    const SizedBox(width: 8),
                                    ElevatedButton(
                                      onPressed: () =>
                                          _handleValidation(user, false),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.red,
                                        padding: const EdgeInsets.all(12),
                                        minimumSize: const Size(50, 50),
                                      ),
                                      child: const Icon(Icons.close,
                                          color: Colors.white),
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
                ),
            ],
          ),
        ),
      ),
    );
  }
}
