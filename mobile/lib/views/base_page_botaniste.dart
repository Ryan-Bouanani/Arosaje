import 'package:flutter/material.dart';
import 'comment_screen.dart';
import '../widgets/custom_bottom_nav_bar_botaniste.dart';
import 'home_after_login_admin.dart';

class BasePageBotaniste extends StatefulWidget {
  final Widget body;
  final int currentIndex;

  const BasePageBotaniste({
    super.key,
    required this.body,
    required this.currentIndex,
  });

  @override
  State<BasePageBotaniste> createState() => _BasePageAdminState();
}

class _BasePageAdminState extends State<BasePageBotaniste> {
  void _onNavigationItemTapped(int index) {
    switch (index) {
      case 0:
        // Si ce n'est pas déjà la page d'accueil
        if (widget.currentIndex != 0) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
                builder: (context) => const HomeAfterLoginAdmin()),
          );
        }
        break;
      case 1:
        if (widget.currentIndex != 1) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const CommentScreen()),
          );
        }
        break;
      case 2:
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.body,
      bottomNavigationBar: CustomBottomNavBarBotaniste(
        currentIndex: widget.currentIndex,
        onTap: _onNavigationItemTapped,
      ),
    );
  }
}
