import 'package:flutter/material.dart';
import 'package:mobile/views/chat_list_screen.dart';
import 'package:mobile/views/settings/settings_page.dart';
import '../widgets/custom_bottom_nav_bar.dart';
import 'plant_current_list_screen.dart';
import 'home_after_login_screen.dart';

// Importez vos autres pages ici

class BasePage extends StatefulWidget {
  final Widget body;
  final int currentIndex;

  const BasePage({
    super.key,
    required this.body,
    required this.currentIndex,
  });

  @override
  State<BasePage> createState() => _BasePageState();
}

class _BasePageState extends State<BasePage> {
  void _onNavigationItemTapped(int index) {
    if (widget.currentIndex == index) return; // Évite de recharger la même page

    switch (index) {
    case 0:
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => const HomeAfterLogin(),
        ),
      );
      break;
    case 1:
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => BasePage(
            body: const PlantCurrentListScreen(),
            currentIndex: 1,
          ),
        ),
      );
      break;
    case 2:
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => BasePage(
            body: const ChatMenuScreen(),
            currentIndex: 2,
          ),
        ),
      );
      break;
    case 3:
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => BasePage(
            body: const SettingsPage(),
            currentIndex: 3,
          ),
        ),
      );
      break;
  }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.body,
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: widget.currentIndex,
        onTap: _onNavigationItemTapped,
      ),
    );
  }
}
