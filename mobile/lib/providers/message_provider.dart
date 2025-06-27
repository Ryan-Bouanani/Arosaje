import 'package:flutter/foundation.dart';
import 'package:mobile/models/conversation.dart';
import 'package:mobile/models/message.dart';
import 'package:mobile/services/message_service.dart';
import 'dart:async';

class MessageProvider extends ChangeNotifier {
  final MessageService _messageService;
  List<Conversation> _conversations = [];
  Map<int, List<Message>> _messages = {};
  Map<int, bool> _typingStatus = {};
  bool _isLoading = false;
  String? _error;
  StreamSubscription<Message>? _messageSubscription;
  StreamSubscription<Map<String, dynamic>>? _typingSubscription;
  StreamSubscription<Map<String, dynamic>>? _readSubscription;
  int? _currentConversationId;

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
      
      // Trier les conversations par date du dernier message (plus récent en premier)
      loadedConversations.sort((a, b) {
        DateTime aDate = a.lastMessage?.createdAt ?? a.updatedAt;
        DateTime bDate = b.lastMessage?.createdAt ?? b.updatedAt;
        return bDate.compareTo(aDate); // Ordre décroissant (plus récent en premier)
      });
      
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
      _error = null;
      notifyListeners();

      // Charger les messages depuis l'API
      if (!_messages.containsKey(conversationId)) {
        _messages[conversationId] = [];
      }

      final List<Message> loadedMessages = await _messageService.getConversationMessages(conversationId);
      // Trier les messages par date de création (du plus ancien au plus récent)
      loadedMessages.sort((a, b) => a.createdAt.compareTo(b.createdAt));
      _messages[conversationId] = loadedMessages;
      notifyListeners();

    } catch (e) {
      _error = e.toString();
      notifyListeners();
      print('Erreur lors du chargement des messages: $e');
    }
  }

  Future<void> connectToWebSocket(int conversationId) async {
    try {
      print('Connecting to WebSocket for conversation $conversationId');
      _currentConversationId = conversationId;
      
      // Fermer les anciennes connexions
      await _closeWebSocketSubscriptions();
      
      // Se connecter au WebSocket
      await _messageService.connectToConversation(conversationId);

      // Écouter les nouveaux messages
      _messageSubscription = _messageService.onMessage.listen((message) {
        print('New message received: ${message.content} for conversation ${message.conversationId}');
        if (message.conversationId == conversationId) {
          if (_messages[conversationId] == null) {
            _messages[conversationId] = [];
          }
          
          // Vérifier si le message n'existe pas déjà
          final existingMessageIndex = _messages[conversationId]!.indexWhere((m) => m.id == message.id);
          if (existingMessageIndex == -1) {
            _messages[conversationId]!.add(message);
            print('Message added to conversation $conversationId. Total messages: ${_messages[conversationId]!.length}');
            notifyListeners();
          } else {
            print('Message already exists, skipping');
          }
        }
      });

      // Écouter les statuts de frappe
      _typingSubscription = _messageService.onTyping.listen((data) {
        if (data['conversation_id'] == conversationId) {
          _typingStatus[conversationId] = data['is_typing'] ?? false;
          notifyListeners();
        }
      });

      // Écouter les marquages de lecture
      _readSubscription = _messageService.onRead.listen((data) {
        if (data['conversation_id'] == conversationId) {
          final messages = _messages[conversationId];
          if (messages != null) {
            bool updated = false;
            for (int i = 0; i < messages.length; i++) {
              if (!messages[i].isRead) {
                // Créer un nouveau message avec isRead = true
                final updatedMessage = Message(
                  id: messages[i].id,
                  content: messages[i].content,
                  senderId: messages[i].senderId,
                  conversationId: messages[i].conversationId,
                  createdAt: messages[i].createdAt,
                  updatedAt: messages[i].updatedAt,
                  isRead: true,
                );
                messages[i] = updatedMessage;
                updated = true;
              }
            }
            if (updated) {
              notifyListeners();
            }
          }
        }
      });
      
      print('WebSocket listeners set up successfully');
      
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      print('Erreur lors de la connexion WebSocket: $e');
    }
  }

  Future<void> _closeWebSocketSubscriptions() async {
    await _messageSubscription?.cancel();
    await _typingSubscription?.cancel();
    await _readSubscription?.cancel();
    _messageSubscription = null;
    _typingSubscription = null;
    _readSubscription = null;
  }

  void sendMessage(int conversationId, String content) {
    print('Sending message: $content');
    _messageService.sendMessage(content);
  }

  void sendTypingStatus(int conversationId, bool isTyping) {
    _messageService.sendTypingStatus(isTyping);
  }

  void markMessagesAsRead(int conversationId) {
    _messageService.markMessagesAsRead();
  }

  void disconnectWebSocket() {
    print('Disconnecting WebSocket');
    _messageService.disconnect();
    _closeWebSocketSubscriptions();
    _currentConversationId = null;
  }

  @override
  void dispose() {
    _closeWebSocketSubscriptions();
    _messageService.dispose();
    super.dispose();
  }
} 