import 'package:flutter/material.dart';
import '../widgets/custom_bottom_nav_bar.dart'; // Assurez-vous que ce chemin est correct

class BasePage extends StatelessWidget {
  final Widget body;
  final int currentIndex;

  const BasePage({
    super.key, // Utilisation du super paramètre pour 'key'
    required this.body,
    required this.currentIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: body,
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: currentIndex,
        onTap: (index) {
          // Logique pour changer de page
        },
      ),
    );
  }
}
