import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import 'home_screen.dart';
import 'home_after_login_screen.dart';
import 'botanist_advice_main_screen.dart';
import 'admin_dashboard.dart';

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({Key? key}) : super(key: key);

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoading = true;
  bool _isAuthenticated = false;
  String? _userRole;

  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    try {
      // Vérifier si un token existe
      final apiService = ApiService();
      final token = await apiService.getToken();
      
      
      if (token == null) {
        setState(() {
          _isLoading = false;
          _isAuthenticated = false;
        });
        return;
      }

      // Vérifier le rôle stocké en SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      final userRole = prefs.getString('user_role');
      
      if (userRole != null) {
        setState(() {
          _isLoading = false;
          _isAuthenticated = true;
          _userRole = userRole;
        });
      } else {
        await apiService.clearToken();
        setState(() {
          _isLoading = false;
          _isAuthenticated = false;
        });
      }
      
    } catch (e) {
      print('[AuthWrapper] Auth check failed: $e');
      // En cas d'erreur, on déconnecte pour être sûr
      try {
        final apiService = ApiService();
        await apiService.clearToken();
      } catch (_) {}
      
      setState(() {
        _isLoading = false;
        _isAuthenticated = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(
                color: Colors.green,
              ),
              SizedBox(height: 16),
              Text(
                'Vérification de l\'authentification...',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (!_isAuthenticated) {
      return const AccueilPage();
    }

    // Utilisateur authentifié, rediriger selon le rôle
    final upperRole = _userRole?.toUpperCase();
    
    switch (upperRole) {
      case 'ADMIN':
        return const AdminDashboard();
      case 'BOTANIST':
        return const BotanistAdviceMainScreen();
      case 'USER':
      default:
        return const HomeAfterLogin();
    }
  }
}
