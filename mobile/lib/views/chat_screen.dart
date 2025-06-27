import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:mobile/providers/message_provider.dart';
import 'package:mobile/models/message.dart';
import 'package:mobile/models/conversation.dart';
import 'package:mobile/services/user_service.dart';
import 'package:mobile/services/api_service.dart';

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
  UserService? _userService;
  int _previousMessageCount = 0;
  Conversation? _currentConversation;
  int? _currentUserId; // Cache de l'ID utilisateur

  @override
  void initState() {
    super.initState();
    _initializeChat();
  }

    Future<void> _initializeChat() async {
    // Initialiser le UserService
    _userService = UserService(ApiService());
    
    // Récupérer l'ID utilisateur une seule fois au début
    try {
      final userService = _userService!;
      final userData = await userService.getCurrentUser();
      if (userData != null && userData['id'] != null) {
        _currentUserId = userData['id'];
      }
    } catch (e) {
      // En cas d'erreur, on laisse _currentUserId à null
    }
    
    if (mounted) {
      final provider = context.read<MessageProvider>();
      
      // Si les conversations ne sont pas encore chargées, les charger d'abord
      if (provider.conversations.isEmpty) {
        await provider.loadConversations();
      }
      
      // Trouver la conversation courante dans la liste
      final conversations = provider.conversations;
      try {
        _currentConversation = conversations.firstWhere(
          (conv) => conv.id == widget.conversationId,
        );
      } catch (e) {
        // Si la conversation n'est pas trouvée, on continue sans
      }
      
      await provider.loadMessages(widget.conversationId);
      await provider.connectToWebSocket(widget.conversationId);
      
      // Marquer les messages comme lus
      provider.markMessagesAsRead(widget.conversationId);
      
      // Scroll initial vers le bas
      WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
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
      
      // Scroll vers le bas après l'envoi d'un message
      WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
    }
  }

  String _getConversationTitle() {
    if (_currentConversation != null) {
      return _currentConversation!.getTitle(_currentUserId ?? 0); // Utiliser l'ID utilisateur réel
    }
    return 'Conversation';
  }

  String _getConversationSubtitle() {
    if (_currentConversation != null) {
      return _currentConversation!.getSubtitle(_currentUserId ?? 0); // Utiliser l'ID utilisateur réel
    }
    return '';
  }

  String _formatMessageTime(DateTime dateTime) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final messageDate = DateTime(dateTime.year, dateTime.month, dateTime.day);
    
    if (messageDate == today) {
      // Aujourd'hui - afficher seulement l'heure
      return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else if (messageDate == today.subtract(const Duration(days: 1))) {
      // Hier
      return 'Hier ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else if (messageDate.isAfter(today.subtract(const Duration(days: 7)))) {
      // Cette semaine - afficher le jour et l'heure
      final days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
      return '${days[dateTime.weekday - 1]} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else {
      // Plus ancien - afficher la date courte et l'heure
      return '${dateTime.day.toString().padLeft(2, '0')}/${dateTime.month.toString().padLeft(2, '0')} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
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
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _getConversationTitle(),
              style: const TextStyle(
                color: Colors.black,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (_getConversationSubtitle().isNotEmpty)
              Text(
                _getConversationSubtitle(),
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
          ],
        ),
        backgroundColor: Colors.white,
        elevation: 1,
        toolbarHeight: _getConversationSubtitle().isNotEmpty ? 70 : 56,
      ),
      body: Column(
        children: [
          Expanded(
            child: Consumer<MessageProvider>(
              builder: (context, provider, child) {
                final messages = provider.getMessages(widget.conversationId);
                final isTyping = provider.isUserTyping(widget.conversationId);

                // Détecter l'ajout de nouveaux messages et scroll automatiquement
                if (messages.length > _previousMessageCount) {
                  _previousMessageCount = messages.length;
                  WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
                }

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
                            onPressed: () async {
                              await provider.loadMessages(widget.conversationId);
                              await provider.connectToWebSocket(widget.conversationId);
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

                // Afficher le message de conversation vide si aucun message
                if (messages.isEmpty && _currentConversation != null) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            _currentConversation!.type == ConversationType.plantCare 
                                ? Icons.eco 
                                : Icons.lightbulb,
                            size: 64,
                            color: Colors.grey[400],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            _currentConversation!.getEmptyMessage(0),
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                    ),
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
                        
                        // Utiliser le cache pour éviter les appels répétés
                        final isCurrentUser = _currentUserId != null && message.senderId == _currentUserId;
                            
                            return Container(
                          margin: const EdgeInsets.symmetric(vertical: 3),
                          child: Row(
                            mainAxisAlignment: isCurrentUser
                                ? MainAxisAlignment.end
                                : MainAxisAlignment.start,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              // Avatar pour les autres utilisateurs (à gauche)
                              if (!isCurrentUser) ...[
                                CircleAvatar(
                                  backgroundColor: Colors.grey[400],
                                  radius: 18,
                                  child: const Icon(
                                    Icons.person,
                                    color: Colors.white, 
                                    size: 20
                                  ),
                                ),
                                const SizedBox(width: 8),
                              ],
                              
                              // Bulle de message
                              Flexible(
                                child: Container(
                                  constraints: BoxConstraints(
                                    maxWidth: MediaQuery.of(context).size.width * 0.7,
                                  ),
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 14,
                                    vertical: 10,
                                  ),
                                  decoration: BoxDecoration(
                                    color: isCurrentUser
                                        ? const Color(0xFF128C7E) // Vert plus doux, moins agressif
                                        : const Color(0xFFE5E5EA), // Gris clair pour les autres
                                    borderRadius: BorderRadius.only(
                                      topLeft: const Radius.circular(20),
                                      topRight: const Radius.circular(20),
                                      bottomLeft: isCurrentUser 
                                          ? const Radius.circular(20) 
                                          : const Radius.circular(6),
                                      bottomRight: isCurrentUser 
                                          ? const Radius.circular(6) 
                                          : const Radius.circular(20),
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withOpacity(0.1),
                                        blurRadius: 2,
                                        offset: const Offset(0, 1),
                                      ),
                                    ],
                                  ),
                                  child: Column(
                                    crossAxisAlignment: isCurrentUser 
                                        ? CrossAxisAlignment.end 
                                        : CrossAxisAlignment.start,
                                    children: [
                                      // Contenu du message
                                      Text(
                                        message.content,
                                        style: TextStyle(
                                          color: isCurrentUser
                                              ? Colors.white
                                              : Colors.black87,
                                          fontSize: 16,
                                          height: 1.3,
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      
                                      // Heure et indicateur de lecture
                                      Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Text(
                                            _formatMessageTime(message.createdAt),
                                            style: TextStyle(
                                              color: isCurrentUser
                                                  ? Colors.white.withOpacity(0.7)
                                                  : Colors.grey[600],
                                              fontSize: 12,
                                              fontWeight: FontWeight.w400,
                                            ),
                                          ),
                                          
                                          // Indicateur de lecture uniquement pour les messages de l'utilisateur actuel
                                          if (isCurrentUser) ...[
                                            const SizedBox(width: 6),
                                            Icon(
                                              message.isRead 
                                                  ? Icons.done_all // Double coche pour "lu"
                                                  : Icons.done, // Simple coche pour "envoyé"
                                              size: 16,
                                              color: message.isRead 
                                                  ? const Color(0xFF34B7F1) // Bleu WhatsApp pour "lu"
                                                  : Colors.white.withOpacity(0.7), // Blanc transparent pour "envoyé"
                                            ),
                                          ],
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                              
                              // Avatar pour l'utilisateur actuel (à droite)
                              if (isCurrentUser) ...[
                                const SizedBox(width: 8),
                                CircleAvatar(
                                  backgroundColor: const Color(0xFF128C7E), // Même vert que la bulle
                                  radius: 18,
                                  child: const Icon(
                                    Icons.account_circle,
                                    color: Colors.white,
                                    size: 20,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        );
                      },
                    ),
                    if (isTyping)
                      Positioned(
                        bottom: 8,
                        left: 24,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.grey[200],
                            borderRadius: BorderRadius.circular(18),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.1),
                                blurRadius: 4,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const CircleAvatar(
                                backgroundColor: Colors.grey,
                                radius: 12,
                                child: Icon(Icons.person,
                                    color: Colors.white, size: 16),
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                'En train d\'écrire',
                                style: TextStyle(
                                  color: Colors.black87,
                                  fontSize: 13,
                                ),
                              ),
                                                             const SizedBox(width: 4),
                               const TypingIndicator(),
                            ],
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
                    onSubmitted: (_) => _handleSendMessage(),
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

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({super.key});

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _animation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _animationController.repeat(reverse: true);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(3, (index) {
            return Container(
              margin: const EdgeInsets.symmetric(horizontal: 1),
              width: 4,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[600]!.withOpacity(
                  index == 0
                      ? _animation.value
                      : index == 1
                          ? _animation.value * 0.8
                          : _animation.value * 0.6,
                ),
                shape: BoxShape.circle,
              ),
            );
          }),
        );
      },
    );
  }
}
