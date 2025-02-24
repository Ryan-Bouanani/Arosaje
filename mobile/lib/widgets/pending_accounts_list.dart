import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../models/user.dart';

class PendingAccountsList extends StatefulWidget {
  const PendingAccountsList({super.key});

  @override
  State<PendingAccountsList> createState() => _PendingAccountsListState();
}

class _PendingAccountsListState extends State<PendingAccountsList> {
  final AuthService _authService = AuthService();
  List<User> _pendingAccounts = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadPendingAccounts();
  }

  Future<void> _loadPendingAccounts() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });
      
      final accounts = await _authService.getPendingAccounts();
      setState(() {
        _pendingAccounts = accounts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = "Erreur lors du chargement des comptes : $e";
        _isLoading = false;
      });
    }
  }

  Future<void> _verifyAccount(User user) async {
    try {
      await _authService.verifyAccount(user.id);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Compte validé avec succès")),
      );
      await _loadPendingAccounts();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Erreur lors de la validation : $e")),
      );
    }
  }

  Future<void> _rejectAccount(User user) async {
    try {
      await _authService.rejectAccount(user.id);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Compte rejeté avec succès")),
      );
      await _loadPendingAccounts();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Erreur lors du rejet : $e")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_error!, style: const TextStyle(color: Colors.red)),
            ElevatedButton(
              onPressed: _loadPendingAccounts,
              child: const Text("Réessayer"),
            ),
          ],
        ),
      );
    }

    if (_pendingAccounts.isEmpty) {
      return const Center(
        child: Text("Aucun compte en attente de validation"),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadPendingAccounts,
      child: ListView.builder(
        itemCount: _pendingAccounts.length,
        itemBuilder: (context, index) {
          final user = _pendingAccounts[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ListTile(
              title: Text("${user.prenom} ${user.nom}"),
              subtitle: Text(user.email),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.check_circle, color: Colors.green),
                    onPressed: () => _verifyAccount(user),
                  ),
                  IconButton(
                    icon: const Icon(Icons.cancel, color: Colors.red),
                    onPressed: () => _rejectAccount(user),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
} 