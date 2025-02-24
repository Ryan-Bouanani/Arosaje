import 'package:flutter/material.dart';
import 'chat_screen.dart';

class ChatMenuScreen extends StatelessWidget {
  const ChatMenuScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Map<String, dynamic>> conversations = [
      {
        'userName': 'Marie Dupont',
        'plantName': 'Orchidée',
        'lastMessage': 'Nickel on fait comme ça, j\'attend votre invitation',
        'time': '14:30',
        'userAvatar': 'assets/images/avatar1.jpg',
        'unreadCount': 2,
      },
      {
        'userName': 'Pierre Martin',
        'plantName': 'Monstera',
        'lastMessage': 'D\'accord pour les dates proposées',
        'time': 'Hier',
        'userAvatar': 'assets/images/avatar2.jpg',
        'unreadCount': 0,
      },
      {
        'userName': 'Sophie Bernard',
        'plantName': 'Ficus',
        'lastMessage': 'Merci pour votre aide',
        'time': '21/03',
        'userAvatar': 'assets/images/avatar3.jpg',
        'unreadCount': 0,
      },
    ];

    return Scaffold(
  appBar: AppBar(
    title: const Text(
      'Messages',
      style: TextStyle(color: Colors.black),
    ),
    backgroundColor: Colors.white,
    elevation: 1,
  ),
  body: ListView.separated(
    itemCount: conversations.length,
    separatorBuilder: (context, index) => const Divider(height: 1),
    itemBuilder: (context, index) {
      final conversation = conversations[index];
      return ListTile(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ChatScreen(),
            ),
          );
        },
        leading: CircleAvatar(
          backgroundColor: Colors.green,
          radius: 25,
          child: Text(
            conversation['plantName'].substring(0, 1),
            style: const TextStyle(color: Colors.white),
          ),
        ),
        title: Row(
          children: [
            Expanded(
              child: RichText(
                text: TextSpan(
                  children: [
                    TextSpan(
                      text: conversation['plantName'],
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.black,
                        fontSize: 16,
                      ),
                    ),
                    TextSpan(
                      text: ' - ${conversation['userName']}',
                      style: const TextStyle(
                        color: Colors.black,
                        fontWeight: FontWeight.normal,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Text(
              conversation['time'],
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              conversation['lastMessage'],
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 13,
              ),
            ),
          ],
        ),
        trailing: conversation['unreadCount'] > 0
            ? Container(
                padding: const EdgeInsets.all(6),
                decoration: const BoxDecoration(
                  color: Colors.green,
                  shape: BoxShape.circle,
                ),
                child: Text(
                  conversation['unreadCount'].toString(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                  ),
                ),
              )
            : null,
      );
    },
  ),
);

  }
}
