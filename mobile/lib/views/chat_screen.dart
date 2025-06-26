import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:mobile/providers/message_provider.dart';
import 'package:mobile/models/message.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ChatScreen extends StatefulWidget {
  final int conversationId;

  const ChatScreen({
    super.key,
    required this.conversationId,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  int? _currentUserId;

  @override
  void initState() {
    super.initState();
    _initializeChat();
  }

  Future<void> _initializeChat() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _currentUserId = prefs.getInt('user_id');
    });

    if (mounted) {
      context.read<MessageProvider>().loadMessages(widget.conversationId);
      context.read<MessageProvider>().connectToWebSocket(widget.conversationId);
    }
  }

  @override
  void dispose() {
    context.read<MessageProvider>().disconnectWebSocket();
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  void _handleSendMessage() {
    if (_messageController.text.trim().isNotEmpty) {
      context
          .read<MessageProvider>()
          .sendMessage(widget.conversationId, _messageController.text.trim());
      _messageController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
          color: Colors.black,
        ),
        title: const Text(
          'Conversation',
          style: TextStyle(color: Colors.black),
        ),
        backgroundColor: Colors.white,
        elevation: 1,
      ),
      body: Column(
        children: [
          Expanded(
            child: Consumer<MessageProvider>(
              builder: (context, provider, child) {
                final messages = provider.getMessages(widget.conversationId);
                final isTyping = provider.isUserTyping(widget.conversationId);

                if (provider.error != null) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.error_outline,
                            size: 64,
                            color: Colors.red,
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            'Erreur de connexion',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.red,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            provider.error!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.grey),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () {
                              provider.loadMessages(widget.conversationId);
                              provider.connectToWebSocket(widget.conversationId);
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                            ),
                            child: const Text('Réessayer'),
                          ),
                          const SizedBox(height: 8),
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(),
                            child: const Text('Retour'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                if (provider.isLoading) {
                  return const Center(
                    child: CircularProgressIndicator(),
                  );
                }

                return Stack(
                  children: [
                    ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.all(16),
                      itemCount: messages.length,
                      itemBuilder: (context, index) {
                        final message = messages[index];
                        final isCurrentUser = message.senderId == _currentUserId;

                        return Container(
                          margin: const EdgeInsets.symmetric(vertical: 8),
                          child: Row(
                            mainAxisAlignment: isCurrentUser
                                ? MainAxisAlignment.end
                                : MainAxisAlignment.start,
                            children: [
                              if (!isCurrentUser)
                                const CircleAvatar(
                                  backgroundColor: Colors.grey,
                                  radius: 16,
                                  child: Icon(Icons.person,
                                      color: Colors.white, size: 20),
                                ),
                              const SizedBox(width: 8),
                              Container(
                                constraints: BoxConstraints(
                                  maxWidth:
                                      MediaQuery.of(context).size.width * 0.7,
                                ),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 10,
                                ),
                                decoration: BoxDecoration(
                                  color: isCurrentUser
                                      ? Colors.green
                                      : Colors.grey[200],
                                  borderRadius: BorderRadius.circular(20),
                                ),
                                child: Text(
                                  message.content,
                                  style: TextStyle(
                                    color: isCurrentUser
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
                    if (isTyping)
                      Positioned(
                        bottom: 0,
                        left: 16,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.black54,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            'En train d\'écrire...',
                            style: TextStyle(color: Colors.white),
                          ),
                        ),
                      ),
                  ],
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
                    onChanged: (value) {
                      context
                          .read<MessageProvider>()
                          .sendTypingStatus(widget.conversationId, value.isNotEmpty);
                    },
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
