import 'package:flutter/material.dart';
import 'package:mobile/services/auth_service.dart';
import 'package:mobile/views/login_screen.dart';

class InscriptionPage extends StatefulWidget {
  const InscriptionPage({super.key});

  @override
  State<InscriptionPage> createState() => _InscriptionPageState();
}

class _InscriptionPageState extends State<InscriptionPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nomController = TextEditingController();
  final _prenomController = TextEditingController();
  final _telephoneController = TextEditingController();
  bool _obscurePassword = true;
  bool _isLoading = false;
  bool _acceptConditions = false;
  String _selectedRole = 'USER';
  late Future<AuthService> _authServiceFuture;

  @override
  void initState() {
    super.initState();
    _authServiceFuture = AuthService.getInstance();
  }

  void _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;
    
    if (!_acceptConditions) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Veuillez accepter les conditions d\'utilisation'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final authService = await _authServiceFuture;
      // Convertir le rôle au format attendu par le backend
      final String backendRole = _selectedRole == 'BOTANIST' ? 'botanist' : 'user';
      
      await authService.register(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        nom: _nomController.text.trim(),
        prenom: _prenomController.text.trim(),
        telephone: _telephoneController.text.trim(),
        role: backendRole,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Inscription réussie ! Vous pouvez maintenant vous connecter.'),
          backgroundColor: Colors.green,
        ),
      );

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const LoginScreen()),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString()),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _nomController.dispose();
    _prenomController.dispose();
    _telephoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            Stack(
              children: [
                Image.asset(
                  'assets/background.jpg',
                  height: 300,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
                Positioned(
                  top: 40,
                  left: 10,
                  child: IconButton(
                    icon: const Icon(Icons.arrow_back, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
                Positioned(
                  bottom: -1,
                  left: 0,
                  right: 0,
                  child: Container(
                    height: 50,
                    decoration: const BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(30),
                        topRight: Radius.circular(30),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text(
                      'Créer un compte',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1B4332),
                      ),
                    ),
                    const SizedBox(height: 32),
                    
                    // Sélection du rôle
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Type de compte',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1B4332),
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: GestureDetector(
                                  onTap: () {
                                    setState(() {
                                      _selectedRole = 'USER';
                                    });
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: _selectedRole == 'USER' 
                                          ? Colors.green.shade100 
                                          : Colors.white,
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(
                                        color: _selectedRole == 'USER'
                                            ? Colors.green
                                            : Colors.grey.shade300,
                                        width: 2,
                                      ),
                                    ),
                                    child: Column(
                                      children: [
                                        Icon(
                                          Icons.person,
                                          color: _selectedRole == 'USER'
                                              ? Colors.green
                                              : Colors.grey,
                                          size: 32,
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          'Particulier',
                                          style: TextStyle(
                                            color: _selectedRole == 'USER'
                                                ? Colors.green
                                                : Colors.grey,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: GestureDetector(
                                  onTap: () {
                                    setState(() {
                                      _selectedRole = 'BOTANIST';
                                    });
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: _selectedRole == 'BOTANIST'
                                          ? Colors.green.shade100
                                          : Colors.white,
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(
                                        color: _selectedRole == 'BOTANIST'
                                            ? Colors.green
                                            : Colors.grey.shade300,
                                        width: 2,
                                      ),
                                    ),
                                    child: Column(
                                      children: [
                                        Icon(
                                          Icons.local_florist,
                                          color: _selectedRole == 'BOTANIST'
                                              ? Colors.green
                                              : Colors.grey,
                                          size: 32,
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          'Botaniste',
                                          style: TextStyle(
                                            color: _selectedRole == 'BOTANIST'
                                                ? Colors.green
                                                : Colors.grey,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    _buildTextField(
                      controller: _emailController,
                      hintText: 'Email',
                      icon: Icons.email_outlined,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Veuillez entrer votre email';
                        }
                        if (!value.contains('@')) {
                          return 'Veuillez entrer un email valide';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _passwordController,
                      hintText: 'Mot de passe',
                      icon: Icons.lock_outline,
                      obscureText: _obscurePassword,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Veuillez entrer votre mot de passe';
                        }
                        if (value.length < 6) {
                          return 'Le mot de passe doit contenir au moins 6 caractères';
                        }
                        return null;
                      },
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscurePassword ? Icons.visibility : Icons.visibility_off,
                          color: Colors.green,
                        ),
                        onPressed: () {
                          setState(() {
                            _obscurePassword = !_obscurePassword;
                          });
                        },
                      ),
                    ),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _nomController,
                      hintText: 'Nom',
                      icon: Icons.person_outline,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Veuillez entrer votre nom';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _prenomController,
                      hintText: 'Prénom',
                      icon: Icons.person_outline,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Veuillez entrer votre prénom';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _telephoneController,
                      hintText: 'Téléphone',
                      icon: Icons.phone_outlined,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Veuillez entrer votre numéro de téléphone';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // Case à cocher des conditions d'utilisation
                    CheckboxListTile(
                      value: _acceptConditions,
                      onChanged: (value) {
                        setState(() {
                          _acceptConditions = value!;
                        });
                      },
                      title: const Text(
                        'J\'accepte les conditions d\'utilisation',
                        style: TextStyle(fontSize: 14),
                      ),
                      activeColor: Colors.green,
                      contentPadding: EdgeInsets.zero,
                      controlAffinity: ListTileControlAffinity.leading,
                    ),
                    
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: _isLoading ? null : _handleRegister,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: _isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text(
                              'S\'inscrire',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text("Déjà inscrit ? "),
                        TextButton(
                          onPressed: () {
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const LoginScreen(),
                              ),
                            );
                          },
                          child: const Text(
                            'Se connecter',
                            style: TextStyle(color: Colors.green),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String hintText,
    required IconData icon,
    bool obscureText = false,
    String? Function(String?)? validator,
    Widget? suffixIcon,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: TextFormField(
        controller: controller,
        obscureText: obscureText,
        validator: validator,
        decoration: InputDecoration(
          hintText: hintText,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          prefixIcon: Icon(icon, color: Colors.green),
          suffixIcon: suffixIcon,
          filled: true,
          fillColor: Colors.transparent,
        ),
      ),
    );
  }
}
