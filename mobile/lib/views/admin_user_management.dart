import 'package:flutter/material.dart';
import 'package:mobile/views/inscription_validation_screen.dart';
import 'package:mobile/services/auth_service.dart';
import 'package:mobile/models/user.dart';

class AdminUserManagement extends StatefulWidget {
  const AdminUserManagement({super.key});

  @override
  State<AdminUserManagement> createState() => _AdminUserManagementState();
}

class _AdminUserManagementState extends State<AdminUserManagement> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late final AuthService _authService;
  List<User> _verifiedUsers = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _initializeService();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _initializeService() async {
    try {
      _authService = await AuthService.getInstance();
      await _loadVerifiedUsers();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadVerifiedUsers() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final users = await _authService.getVerifiedUsers();
      setState(() {
        _verifiedUsers = users;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _showChangeRoleDialog(User user) {
    String selectedRole = user.role;
    final availableRoles = ['USER', 'BOTANIST', 'ADMIN'];
    
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: Text('Changer le rôle de ${user.prenom} ${user.nom}'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Rôle actuel: ${user.role}'),
                  const SizedBox(height: 16),
                  DropdownButton<String>(
                    value: selectedRole,
                    isExpanded: true,
                    items: availableRoles.map((String role) {
                      return DropdownMenuItem<String>(
                        value: role,
                        child: Text(role),
                      );
                    }).toList(),
                    onChanged: (String? newRole) {
                      if (newRole != null) {
                        setDialogState(() {
                          selectedRole = newRole;
                        });
                      }
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Annuler'),
                ),
                ElevatedButton(
                  onPressed: selectedRole == user.role
                      ? null
                      : () => _changeUserRole(user, selectedRole),
                  child: const Text('Confirmer'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _changeUserRole(User user, String newRole) async {
    try {
      Navigator.of(context).pop(); // Fermer la dialog
      
      // Afficher un loading
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Row(
            children: [
              CircularProgressIndicator(color: Colors.white),
              SizedBox(width: 16),
              Text('Changement de rôle en cours...'),
            ],
          ),
        ),
      );

      await _authService.changeUserRole(user.id, newRole);
      
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Rôle de ${user.prenom} ${user.nom} changé vers $newRole'),
          backgroundColor: Colors.green,
        ),
      );
      
      // Recharger la liste
      await _loadVerifiedUsers();
      
    } catch (e) {
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erreur lors du changement de rôle: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Widget _buildVerifiedUsersTab() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_error!, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadVerifiedUsers,
              child: const Text("Réessayer"),
            ),
          ],
        ),
      );
    }

    if (_verifiedUsers.isEmpty) {
      return const Center(child: Text("Aucun utilisateur validé"));
    }

    return RefreshIndicator(
      onRefresh: _loadVerifiedUsers,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _verifiedUsers.length,
        itemBuilder: (context, index) {
          final user = _verifiedUsers[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              title: Text("${user.prenom} ${user.nom}"),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(user.email),
                  Text("Rôle: ${user.role}", style: TextStyle(color: Colors.grey[600])),
                ],
              ),
              trailing: PopupMenuButton<String>(
                onSelected: (value) {
                  switch (value) {
                    case 'role':
                      _showChangeRoleDialog(user);
                      break;
                  }
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'role',
                    child: Row(
                      children: [
                        Icon(Icons.edit),
                        SizedBox(width: 8),
                        Text('Changer rôle'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Gestion Utilisateurs',
          style: TextStyle(color: Colors.black),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'En attente'),
            Tab(text: 'Validés'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          const InscriptionValidationScreen(showAppBar: false),
          _buildVerifiedUsersTab(),
        ],
      ),
    );
  }
}
