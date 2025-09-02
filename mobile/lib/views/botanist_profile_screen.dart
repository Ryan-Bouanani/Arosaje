import 'package:flutter/material.dart';
import 'package:mobile/widgets/logout_dialog.dart';
import 'package:mobile/views/login_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/services/auth_service.dart';
import 'package:mobile/services/unified_advice_service.dart';
import 'package:mobile/services/profile_service.dart';
import 'package:mobile/models/user.dart';
import 'package:mobile/services/storage_service.dart';
import 'base_page_botaniste.dart';
import '../models/advice.dart';
import 'package:provider/provider.dart';
import 'package:mobile/providers/message_provider.dart';

class BotanistProfileScreen extends StatefulWidget {
  const BotanistProfileScreen({super.key});

  @override
  State<BotanistProfileScreen> createState() => _BotanistProfileScreenState();
}

class _BotanistProfileScreenState extends State<BotanistProfileScreen> {
  User? _user;
  bool _isLoading = true;
  String? _error;
  final ProfileService _profileService = ProfileService();
  late final UnifiedAdviceService _plantCareAdviceService;
  AdviceStats? _stats;

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    _plantCareAdviceService = await UnifiedAdviceService.init();
    _loadUserData();
    _loadBotanistStats();
  }

  Future<void> _loadUserData() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final authService = await AuthService.getInstance();
      final storageService = await StorageService.init();
      final token = storageService.getToken();
      
      if (token == null) {
        throw Exception('Non authentifié');
      }

      final userData = await authService.getCurrentUser(token);
      
      setState(() {
        _user = User.fromJson(userData);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadBotanistStats() async {
    try {
      final adviceStats = await _plantCareAdviceService.getAdviceStats();
      
      setState(() {
        _stats = adviceStats;
      });
    } catch (e) {
      // Gérer silencieusement l'erreur des stats
      setState(() {
        _stats = AdviceStats(
          totalToReview: 0,
          totalReviewed: 0,
          urgentCount: 0,
          followUpCount: 0,
          pendingValidation: 0,
          myAdviceCount: 0,
        );
      });
    }
  }

  Future<void> _handleLogout(BuildContext context) async {
    final bool shouldLogout = await showLogoutConfirmationDialog(context);
    if (shouldLogout) {
      try {
        // Vider le cache des conversations avant la déconnexion
        if (context.mounted) {
          Provider.of<MessageProvider>(context, listen: false).clearCache();
        }
        
        final authService = await AuthService.getInstance();
        await authService.logout();
        
        if (context.mounted) {
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (context) => const LoginScreen()),
            (route) => false,
          );
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Erreur lors de la déconnexion : $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return BasePageBotaniste(
      currentIndex: 3,
      body: Scaffold(
        appBar: AppBar(
          title: const Text("Profil Botaniste"),
          backgroundColor: Colors.green,
          foregroundColor: Colors.white,
          automaticallyImplyLeading: false,
        ),
        body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Erreur: $_error',
                      style: const TextStyle(color: Colors.red),
                    ),
                    ElevatedButton(
                      onPressed: _loadUserData,
                      child: const Text('Réessayer'),
                    ),
                  ],
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(16.0),
                children: [
                  // Section Statistiques Botaniste
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Mes Statistiques',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: _buildStatCard(
                                  'Mes Conseils', 
                                  '${_stats?.myAdviceCount ?? 0}', 
                                  Icons.assignment,
                                  Colors.blue,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: _buildStatCard(
                                  'Validés', 
                                  '${_stats?.myValidatedCount ?? 0}', 
                                  Icons.check_circle,
                                  Colors.green,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: _buildStatCard(
                                  'Validations Faites', 
                                  '${_stats?.myValidationsDoneCount ?? 0}', 
                                  Icons.verified_user,
                                  Colors.orange,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Section Informations Personnelles
                  buildListTile(
                    title: "Email",
                    subtitle: _user?.email ?? '',
                    onTap: () => _showChangeEmailDialog(context),
                  ),
                  buildListTile(
                    title: "Nom complet",
                    subtitle: "${_user?.prenom ?? ''} ${_user?.nom ?? ''}",
                    onTap: () => _showChangeFullNameDialog(context),
                  ),
                  buildListTile(
                    title: "Numéro de téléphone",
                    subtitle: _user?.telephone ?? 'Non renseigné',
                    onTap: () => _showChangePhoneDialog(context),
                  ),
                  buildListTile(
                    title: "Ville/Région",
                    subtitle: _user?.localisation ?? 'Non renseignée',
                    onTap: () => _showChangeCityDialog(context),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Section Actions
                  buildListTile(
                    title: "Changer de mot de passe",
                    onTap: () => _showChangePasswordDialog(context),
                  ),
                  buildListTile(
                    title: "Déconnexion",
                    onTap: () => _handleLogout(context),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  ListTile buildListTile({
    required String title,
    String? subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
      onTap: onTap,
      title: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween, 
        children: [
          Expanded(
            child: Text(
              title,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
          ),
          if (subtitle != null)
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.green, 
              ),
            ),
        ],
      ),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16.0, color: Colors.grey),
    );
  }

  // Reprise des méthodes de dialogue de la page de profil existante
  void _showChangePasswordDialog(BuildContext context) {
    final currentPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    final confirmPasswordController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15.0),
          ),
          child: Container(
            padding: const EdgeInsets.all(20.0),
            width: MediaQuery.of(context).size.width * 0.9,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text(
                      "Changer de mot de passe",
                      style: TextStyle(
                        fontSize: 18.0,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20.0),
                _buildTextField(currentPasswordController, "Mot de passe actuel"),
                const SizedBox(height: 10.0),
                _buildTextField(newPasswordController, "Nouveau mot de passe"),
                const SizedBox(height: 10.0),
                _buildTextField(confirmPasswordController, "Confirmez le nouveau mot de passe"),
                const SizedBox(height: 20.0),
                ElevatedButton(
                  onPressed: () async {
                    if (newPasswordController.text != confirmPasswordController.text) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Les mots de passe ne correspondent pas."),
                          backgroundColor: Colors.red,
                        ),
                      );
                      return;
                    }
                    
                    try {
                      await _profileService.changePassword(
                        currentPassword: currentPasswordController.text,
                        newPassword: newPasswordController.text,
                      );
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Mot de passe mis à jour avec succès !"),
                          backgroundColor: Colors.green,
                        ),
                      );
                    } catch (e) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(e.toString().replaceAll('Exception: ', '')),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(vertical: 15.0),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(50),
                    ),
                  ),
                  child: const Text(
                    "Confirmer",
                    style: TextStyle(
                      fontSize: 16.0,
                      fontWeight: FontWeight.w500,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showChangeEmailDialog(BuildContext context) {
    final newEmailController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15.0),
          ),
          child: Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white, 
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text(
                      "Modifier l'adresse e-mail",
                      style: TextStyle(
                        fontSize: 18.0,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20.0),
                _buildTextField(newEmailController, "Saisir nouvelle adresse e-mail"),
                const SizedBox(height: 20.0),
                ElevatedButton(
                  onPressed: () async {
                    if (!newEmailController.text.contains('@')) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Veuillez entrer un email valide"),
                          backgroundColor: Colors.red,
                        ),
                      );
                      return;
                    }
                    
                    try {
                      await _profileService.updateProfile(
                        email: newEmailController.text,
                      );
                      Navigator.pop(context);
                      await _loadUserData();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Email mis à jour avec succès !"),
                          backgroundColor: Colors.green,
                        ),
                      );
                    } catch (e) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(e.toString().replaceAll('Exception: ', '')),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(vertical: 15.0),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(50),
                    ),
                  ),
                  child: const Text(
                    "Confirmer",
                    style: TextStyle(
                      fontSize: 16.0,
                      fontWeight: FontWeight.w500,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showChangeFullNameDialog(BuildContext context) {
    final fullNameController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15.0),
          ),
          child: Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text(
                      "Modifier le Nom complet",
                      style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
                const SizedBox(height: 20.0),
                _buildTextField(fullNameController, "Entrez votre nouveau nom complet"),
                const SizedBox(height: 20.0),
                ElevatedButton(
                  onPressed: () async {
                    final names = fullNameController.text.trim().split(' ');
                    if (names.isEmpty) return;
                    
                    try {
                      await _profileService.updateProfile(
                        prenom: names.first,
                        nom: names.length > 1 ? names.sublist(1).join(' ') : names.first,
                      );
                      Navigator.pop(context);
                      await _loadUserData();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Nom complet mis à jour avec succès !"),
                          backgroundColor: Colors.green,
                        ),
                      );
                    } catch (e) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(e.toString().replaceAll('Exception: ', '')),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(vertical: 15.0),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(50)),
                  ),
                  child: const Text("Confirmer", style: TextStyle(fontSize: 16.0, color: Colors.white)),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showChangePhoneDialog(BuildContext context) {
    final phoneController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15.0),
          ),
          child: Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text(
                      "Modifier le Numéro de téléphone",
                      style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
                const SizedBox(height: 20.0),
                _buildTextField(phoneController, "Entrez votre nouveau numéro"),
                const SizedBox(height: 20.0),
                ElevatedButton(
                  onPressed: () async {
                    try {
                      await _profileService.updateProfile(
                        telephone: phoneController.text,
                      );
                      Navigator.pop(context);
                      await _loadUserData();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Numéro mis à jour avec succès !"),
                          backgroundColor: Colors.green,
                        ),
                      );
                    } catch (e) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(e.toString().replaceAll('Exception: ', '')),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(vertical: 15.0),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(50)),
                  ),
                  child: const Text("Confirmer", style: TextStyle(fontSize: 16.0, color: Colors.white)),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showChangeCityDialog(BuildContext context) {
    final cityController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15.0),
          ),
          child: Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text(
                      "Modifier la Ville",
                      style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
                const SizedBox(height: 20.0),
                _buildTextField(cityController, "Entrez votre nouvelle ville"),
                const SizedBox(height: 20.0),
                ElevatedButton(
                  onPressed: () async {
                    try {
                      await _profileService.updateProfile(
                        localisation: cityController.text,
                      );
                      Navigator.pop(context);
                      await _loadUserData();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Ville mise à jour avec succès !"),
                          backgroundColor: Colors.green,
                        ),
                      );
                    } catch (e) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(e.toString().replaceAll('Exception: ', '')),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(vertical: 15.0),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(50)),
                  ),
                  child: const Text("Confirmer", style: TextStyle(fontSize: 16.0, color: Colors.white)),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTextField(TextEditingController controller, String hintText) {
    return Container(
      decoration: BoxDecoration(
        color: const Color.fromRGBO(18, 156, 82, 0.10), 
        borderRadius: BorderRadius.circular(50), 
      ),
      padding: const EdgeInsets.symmetric(horizontal: 25.0),
      child: TextField(
        controller: controller,
        decoration: InputDecoration(
          hintText: hintText,
          border: InputBorder.none, 
          hintStyle: const TextStyle(color: Color.fromRGBO(65, 65, 65, 0.7)),
        ),
      ),
    );
  }
}
