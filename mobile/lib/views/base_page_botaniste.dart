import 'package:flutter/material.dart';
import '../widgets/custom_bottom_nav_bar_botaniste.dart';
import 'botanist_advice_main_screen.dart';
import 'botanist_chat_screen.dart';
import 'botanist_reports_screen.dart';
import 'botanist_profile_screen.dart';

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
        // Gardes
        if (widget.currentIndex != 0) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
                builder: (context) => const BotanistAdviceMainScreen()),
          );
        }
        break;
      case 1:
        // Messages
        if (widget.currentIndex != 1) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const BotanistChatScreen()),
          );
        }
        break;
      case 2:
        // Rapports de Garde
        if (widget.currentIndex != 2) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const BotanistReportsScreen()),
          );
        }
        break;
      case 3:
        // Profil Botaniste
        if (widget.currentIndex != 3) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const BotanistProfileScreen()),
          );
        }
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
