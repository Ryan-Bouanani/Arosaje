import 'package:flutter/foundation.dart';
import 'package:mobile/models/conversation.dart';
import 'package:mobile/models/message.dart';
import 'package:mobile/services/message_service.dart';
import 'package:mobile/services/websocket_manager.dart';
import 'package:mobile/services/api_service.dart';
import 'dart:async';

class MessageProvider extends ChangeNotifier {
  final MessageService _messageService;
  final WebSocketManager _webSocketManager = WebSocketManager();
  final ApiService _apiService = ApiService();
  
  List<Conversation> _conversations = [];
  Map<int, List<Message>> _messages = {};
  Map<int, bool> _typingStatus = {};
  bool _isLoading = false;
  String? _error;
  ConnectionState _connectionState = ConnectionState.disconnected;
  
  StreamSubscription<dynamic>? _messageSubscription;
  StreamSubscription<ConnectionState>? _stateSubscription;
  StreamSubscription<String>? _errorSubscription;
  int? _currentConversationId;

  MessageProvider(this._messageService) {
    _initializeWebSocketListeners();
  }

  List<Conversation> get conversations => _conversations;
  List<Message> getMessages(int conversationId) => _messages[conversationId] ?? [];
  bool isUserTyping(int conversationId) => _typingStatus[conversationId] ?? false;
  bool get isLoading => _isLoading;
  String? get error => _error;
  ConnectionState get connectionState => _connectionState;
  bool get isConnected => _connectionState == ConnectionState.connected;
  
  void _initializeWebSocketListeners() {
    // Écouter les changements d'état de connexion
    _stateSubscription = _webSocketManager.onStateChange.listen((state) {
      _connectionState = state;
      notifyListeners();
    });
    
    // Écouter les erreurs
    _errorSubscription = _webSocketManager.onError.listen((error) {
      _error = error;
      notifyListeners();
    });
  }

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
      // Connexion WebSocket
      _currentConversationId = conversationId;
      
      // Obtenir le token d'authentification
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }
      
      // Se déconnecter de l'ancienne conversation si nécessaire
      if (_webSocketManager.isConnected) {
        await _webSocketManager.disconnect();
      }
      
      // Se connecter à la nouvelle conversation
      await _webSocketManager.connect(
        token: token,
        conversationId: conversationId,
      );
      
      // Écouter les messages WebSocket
      _messageSubscription?.cancel();
      _messageSubscription = _webSocketManager.onMessage.listen((data) {
        _handleWebSocketMessage(data, conversationId);
      });
      
      // WebSocket connecté
      
    } catch (e) {
      // Erreur WebSocket
      _error = e.toString();
      notifyListeners();
    }
  }
  
  void _handleWebSocketMessage(Map<String, dynamic> data, int conversationId) {
    final messageType = data['type'];
    // Message reçu: $messageType
    
    switch (messageType) {
      case 'new_message':
        final messageData = data['message'];
        if (messageData != null && messageData['conversation_id'] == conversationId) {
          final message = Message.fromJson(messageData);
          
          // Ajouter le message s'il n'existe pas déjà
          if (_messages[conversationId] == null) {
            _messages[conversationId] = [];
          }
          
          final existingIndex = _messages[conversationId]!.indexWhere((m) => m.id == message.id);
          if (existingIndex == -1) {
            _messages[conversationId]!.add(message);
            // Trier les messages par date
            _messages[conversationId]!.sort((a, b) => a.createdAt.compareTo(b.createdAt));
            // Message ajouté
            notifyListeners();
          }
        }
        break;
        
      case 'typing_status':
        final convId = data['conversation_id'];
        final isTyping = data['is_typing'] ?? false;
        if (convId == conversationId) {
          _typingStatus[conversationId] = isTyping;
          notifyListeners();
        }
        break;
        
      case 'messages_read':
        final convId = data['conversation_id'];
        if (convId == conversationId && _messages[conversationId] != null) {
          // Marquer tous les messages comme lus
          bool updated = false;
          for (int i = 0; i < _messages[conversationId]!.length; i++) {
            if (!_messages[conversationId]![i].isRead) {
              _messages[conversationId]![i] = Message(
                id: _messages[conversationId]![i].id,
                content: _messages[conversationId]![i].content,
                senderId: _messages[conversationId]![i].senderId,
                conversationId: _messages[conversationId]![i].conversationId,
                createdAt: _messages[conversationId]![i].createdAt,
                updatedAt: _messages[conversationId]![i].updatedAt,
                isRead: true,
              );
              updated = true;
            }
          }
          if (updated) {
            notifyListeners();
          }
        }
        break;
    }
  }

  Future<void> _closeWebSocketSubscriptions() async {
    await _messageSubscription?.cancel();
    await _stateSubscription?.cancel();
    await _errorSubscription?.cancel();
    _messageSubscription = null;
    _stateSubscription = null;
    _errorSubscription = null;
  }

  Future<void> sendMessage(int conversationId, String content) async {
    try {
      // Envoi du message
      
      // Si WebSocket connecté, envoyer via WebSocket
      if (_webSocketManager.isConnected) {
        _webSocketManager.sendMessage({
          'type': 'message',
          'content': content,
          'conversation_id': conversationId,
        });
        // Envoyé via WebSocket
      } else {
        // Sinon, utiliser l'API REST comme fallback
        // Utilisation API REST
        await _messageService.sendMessageViaAPI(conversationId, content);
        
        // Recharger les messages après l'envoi via REST
        await loadMessages(conversationId);
      }
    } catch (e) {
      print('Error sending message: $e');
      _error = e.toString();
      notifyListeners();
    }
  }

  void sendTypingStatus(int conversationId, bool isTyping) {
    if (_webSocketManager.isConnected) {
      _webSocketManager.sendMessage({
        'type': 'typing',
        'is_typing': isTyping,
        'conversation_id': conversationId,
      });
    }
  }

  void markMessagesAsRead(int conversationId) {
    if (_webSocketManager.isConnected) {
      _webSocketManager.sendMessage({
        'type': 'read',
        'conversation_id': conversationId,
      });
    }
  }

  void disconnectWebSocket() {
    // Déconnexion WebSocket
    _webSocketManager.disconnect();
    _closeWebSocketSubscriptions();
    _currentConversationId = null;
  }

  // Méthode pour vider le cache lors du changement d'utilisateur
  void clearCache() {
    _conversations.clear();
    _messages.clear();
    _typingStatus.clear();
    _error = null;
    _isLoading = false;
    disconnectWebSocket();
    notifyListeners();
  }

  @override
  void dispose() {
    _closeWebSocketSubscriptions();
    _webSocketManager.dispose();
    _messageService.dispose();
    super.dispose();
  }
} 