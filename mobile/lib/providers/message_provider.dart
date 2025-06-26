import 'package:flutter/foundation.dart';
import 'package:mobile/models/conversation.dart';
import 'package:mobile/models/message.dart';
import 'package:mobile/services/message_service.dart';

class MessageProvider extends ChangeNotifier {
  final MessageService _messageService;
  List<Conversation> _conversations = [];
  Map<int, List<Message>> _messages = {};
  Map<int, bool> _typingStatus = {};
  bool _isLoading = false;
  String? _error;

  MessageProvider(this._messageService);

  List<Conversation> get conversations => _conversations;
  List<Message> getMessages(int conversationId) => _messages[conversationId] ?? [];
  bool isUserTyping(int conversationId) => _typingStatus[conversationId] ?? false;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadConversations() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final List<Conversation> loadedConversations = await _messageService.getUserConversations();
      _conversations = loadedConversations;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      print('Erreur lors du chargement des conversations: $e');
    }
  }

  Future<void> loadMessages(int conversationId) async {
    try {
      if (!_messages.containsKey(conversationId)) {
        _messages[conversationId] = [];
      }

      final List<Message> loadedMessages = await _messageService.getConversationMessages(conversationId);
      _messages[conversationId] = loadedMessages;
      notifyListeners();

      // Se connecter au WebSocket pour les mises à jour en temps réel
      await _messageService.connectToConversation(conversationId);

      // Écouter les nouveaux messages
      _messageService.onMessage.listen((message) {
        if (message.conversationId == conversationId) {
          if (_messages[conversationId] == null) {
            _messages[conversationId] = [];
          }
          _messages[conversationId]!.add(message);
          notifyListeners();
        }
      });

      // Écouter les statuts de frappe
      _messageService.onTyping.listen((data) {
        if (data['conversation_id'] == conversationId) {
          _typingStatus[conversationId] = data['is_typing'];
          notifyListeners();
        }
      });

      // Écouter les marquages de lecture
      _messageService.onRead.listen((data) {
        if (data['conversation_id'] == conversationId) {
          final messages = _messages[conversationId];
          if (messages != null) {
            for (var message in messages) {
              if (!message.isRead) {
                // Créer un nouveau message avec isRead = true
                final updatedMessage = Message(
                  id: message.id,
                  content: message.content,
                  senderId: message.senderId,
                  conversationId: message.conversationId,
                  createdAt: message.createdAt,
                  updatedAt: message.updatedAt,
                  isRead: true,
                );
                final index = messages.indexOf(message);
                messages[index] = updatedMessage;
              }
            }
            notifyListeners();
          }
        }
      });
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void sendMessage(int conversationId, String content) {
    _messageService.sendMessage(content);
  }

  void sendTypingStatus(int conversationId, bool isTyping) {
    _messageService.sendTypingStatus(isTyping);
  }

  void markMessagesAsRead(int conversationId) {
    _messageService.markMessagesAsRead();
  }

  Future<void> connectToWebSocket(int conversationId) async {
    await _messageService.connectToConversation(conversationId);
  }

  void disconnectWebSocket() {
    _messageService.disconnect();
  }

  @override
  void dispose() {
    _messageService.dispose();
    super.dispose();
  }
} 