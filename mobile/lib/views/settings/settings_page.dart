import 'package:flutter/material.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Paramètre"),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            Navigator.pop(context);
          },
        ),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // User Info Section
            Card(
            margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            color: const Color(0xFFF8FBF8), 
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12.0),
            ),
              child: Column(
                children: [
                  buildListTile(
                    title: "Email",
                    subtitle: "m.yasir.k.2001@gmail.com",
                    onTap: () => _showChangeEmailDialog(context),
                  ),
                  buildListTile(
                    title: "Nom complet",
                    subtitle: "Muhammad Yasir",
                    onTap: () => _showChangeFullNameDialog(context),
                  ),
                  buildListTile(
                    title: "Numéro de téléphone",
                    subtitle: "+33622853074",
                    onTap: () => _showChangePhoneDialog(context),
                  ),
                  buildListTile(
                    title: "Ville",
                    subtitle: "Rillieux-la-Pape",
                    onTap: () => _showChangeCityDialog(context),
                  ),
                ],
              ),
            ),

            // Account Information Section
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              color: const Color(0xFFF8FBF8), 
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Column(
                children: [
                  buildListTile(
                    title: "Plantes enregistrées",
                    onTap: () {},
                  ),
                  buildListTile(
                    title: "Historique des Gardes",
                    onTap: () {},
                  ),
                  buildListTile(
                    title: "Rate Us",
                    onTap: () {},
                  ),
                  buildListTile(
                    title: "Privacy policy",
                    onTap: () {},
                  ),
                  buildListTile(
                    title: "Terms of use",
                    onTap: () {},
                  ),
                  buildListTile(
                    title: "Contact us",
                    onTap: () {},
                  ),
                ],
              ),
            ),
            
            // Change Password Section
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              color: const Color(0xFFF8FBF8), 
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0), 
              ),
              child: buildListTile(
                title: "Changer de mot de passe",
                onTap: () => _showChangePasswordDialog(context),
              ),
            ),
            
            // Logout Section
            Padding(
            padding: const EdgeInsets.only(top: 24.0),
            child: Card(
              margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: buildListTile(
                title: "Déconnexion",
                subtitle: "m.yasir.k.2001@gmail.com",
                onTap: () {},
              ),
            ),
          ),
          ],
        ),
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
                onPressed: () {
                  if (newPasswordController.text == confirmPasswordController.text) {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Mot de passe mis à jour avec succès !"),
                        backgroundColor: Colors.green,
                      ),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Les mots de passe ne correspondent pas."),
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
                onPressed: () {
                  if (newEmailController.text.contains('@')) {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Email mis à jour avec succès !"),
                        backgroundColor: Colors.green,
                      ),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Veuillez entrer un email valide"),
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
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text("Nom complet mis à jour avec succès !"),
                      backgroundColor: Colors.green,
                    ),
                  );
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
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text("Numéro mis à jour avec succès !"),
                      backgroundColor: Colors.green,
                    ),
                  );
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
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text("Ville mise à jour avec succès !"),
                      backgroundColor: Colors.green,
                    ),
                  );
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