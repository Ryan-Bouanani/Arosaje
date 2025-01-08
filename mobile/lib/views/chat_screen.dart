import 'package:flutter/material.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [
    {
      'sender': 'Moi',
      'message':
          'Bonjour, j\'ai vu votre post pour faire garder vos plantes, je serai ravi de vous les garder. Quelle était etait vos date prévue ?',
      'isInvitation': false,
    },
    {
      'sender': 'Propriétaire',
      'message':
          'Bonjour, pas de soucis c\'est ok pour moi, je voudrais vous la faire garder du 20/12/2024 au 24/12/2024. Est-ce que cela vous convient ?',
      'isInvitation': false,
    },
    {
      'sender': 'Moi',
      'message': 'Nickel on fait comme ça, j\'attend votre invitation',
      'isInvitation': false,
    },
    {
      'sender': 'Propriétaire',
      'message': '',
      'isInvitation': true,
      'invitationStartDate': '20/12/2024',
      'invitationEndDate': '24/12/2024',
      'plantName': 'Orchidée',
      'time': '12h à 15h',
    },
  ];

  void _handleSendMessage() {
    if (_messageController.text.trim().isNotEmpty) {
      setState(() {
        _messages.add({
          'sender': 'Moi',
          'message': _messageController.text,
          'isInvitation': false,
        });
      });
      _messageController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
          color: Colors.black,
        ),
        title: const Row(
          children: [
            CircleAvatar(
              backgroundColor: Colors.green,
              radius: 16,
            ),
            SizedBox(width: 8),
            Text(
              'Utilisateur',
              style: TextStyle(color: Colors.black),
            ),
          ],
        ),
        backgroundColor: Colors.white,
        elevation: 1,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                if (message['isInvitation']) {
                  return Card(
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Invitation du ${message['sender']}',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          Text('Plante: ${message['plantName']}'),
                          Text('Debut: ${message['invitationStartDate']}'),
                          Text('Fin: ${message['invitationEndDate']}'),
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              Expanded(
                                child: ElevatedButton(
                                  onPressed: () {},
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green,
                                  ),
                                  child: const Text('Accepter'),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: OutlinedButton(
                                  onPressed: () {},
                                  child: const Text('Refuser'),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                }
                return Container(
                  margin: const EdgeInsets.symmetric(vertical: 8),
                  child: Row(
                    mainAxisAlignment: message['sender'] == 'Moi'
                        ? MainAxisAlignment.end
                        : MainAxisAlignment.start,
                    children: [
                      if (message['sender'] != 'Moi')
                        const CircleAvatar(
                          backgroundColor: Colors.grey,
                          radius: 16,
                          child:
                              Icon(Icons.person, color: Colors.white, size: 20),
                        ),
                      const SizedBox(width: 8),
                      Container(
                        constraints: BoxConstraints(
                          maxWidth: MediaQuery.of(context).size.width * 0.7,
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),
                        decoration: BoxDecoration(
                          color: message['sender'] == 'Moi'
                              ? Colors.green
                              : Colors.grey[200],
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          message['message'],
                          style: TextStyle(
                            color: message['sender'] == 'Moi'
                                ? Colors.white
                                : Colors.black,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withAlpha(200),
                  spreadRadius: 1,
                  blurRadius: 3,
                  offset: const Offset(0, -1),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: 'Écrivez votre message...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _handleSendMessage,
                  color: Colors.green,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
