import 'package:flutter/material.dart';

class InscriptionValidationScreen extends StatefulWidget {
  const InscriptionValidationScreen({super.key});

  @override
  State<InscriptionValidationScreen> createState() =>
      _InscriptionValidationScreenState();
}

class _InscriptionValidationScreenState
    extends State<InscriptionValidationScreen> {
  // Liste simulée des utilisateurs en attente de validation
  final List<Map<String, String>> pendingUsers = [
    {
      'name': 'Utilisateur 1',
      'info': 'info sur l\'utilisateur',
      'role': 'botaniste'
    },
    {
      'name': 'Utilisateur 2',
      'info': 'info sur l\'utilisateur',
      'role': 'botaniste'
    },
    {
      'name': 'Utilisateur 3',
      'info': 'info sur l\'utilisateur',
      'role': 'botaniste'
    },
  ];

  void _handleValidation(int index, bool isApproved) {
    setState(() {
      pendingUsers.removeAt(index);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isApproved
                ? 'Utilisateur validé avec succès'
                : 'Utilisateur refusé avec succès',
          ),
          backgroundColor: isApproved ? Colors.green : Colors.red,
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Validation des inscriptions',
          style: TextStyle(color: Colors.black),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          color: Colors.grey[100],
          border: Border.all(
            color: Colors.blue,
            width: 2,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              const Text(
                'Validation des inscriptions',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              Expanded(
                child: ListView.builder(
                  itemCount: pendingUsers.length,
                  itemBuilder: (context, index) {
                    final user = pendingUsers[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 16),
                      elevation: 2,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    user['name']!,
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(user['info']!),
                                  Text('Role : ${user['role']!}'),
                                ],
                              ),
                            ),
                            Row(
                              children: [
                                ElevatedButton(
                                  onPressed: () =>
                                      _handleValidation(index, true),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green,
                                    padding: const EdgeInsets.all(12),
                                    minimumSize: const Size(50, 50),
                                  ),
                                  child: const Icon(Icons.check,
                                      color: Colors.white),
                                ),
                                const SizedBox(width: 8),
                                ElevatedButton(
                                  onPressed: () =>
                                      _handleValidation(index, false),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.red,
                                    padding: const EdgeInsets.all(12),
                                    minimumSize: const Size(50, 50),
                                  ),
                                  child: const Icon(Icons.close,
                                      color: Colors.white),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
