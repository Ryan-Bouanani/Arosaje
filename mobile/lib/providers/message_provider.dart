import 'package:flutter/foundation.dart';
import 'package:mobile/models/conversation.dart';
import 'package:mobile/models/message.dart';
import 'package:mobile/services/message_service.dart';
import 'package:mobile/services/websocket_manager.dart';
import 'package:mobile/services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:async';
import 'dart:math';

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
  int? _currentUserId;
  Map<String, int> _tempMessageMapping = {}; // Map temporary UUID to conversation ID
  final Random _random = Random();
  
  StreamSubscription<dynamic>? _messageSubscription;
  StreamSubscription<ConnectionState>? _stateSubscription;
  StreamSubscription<String>? _errorSubscription;
  int? _currentConversationId;

  MessageProvider(this._messageService) {
    _initializeWebSocketListeners();
    _loadCurrentUserId();
  }
  
  Future<void> _loadCurrentUserId() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _currentUserId = prefs.getInt('userId');
      print('[MessageProvider] Loaded current user ID: $_currentUserId');
    } catch (e) {
      print('[MessageProvider] Error loading user ID: $e');
    }
  }
  
  // Générer un UUID unique pour les messages temporaires
  String _generateTempId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final randomPart = _random.nextInt(999999);
    return 'temp_${timestamp}_$randomPart';
  }
  
  // Normaliser le contenu pour comparaison
  String _normalizeContent(String content) {
    return content.trim().replaceAll(RegExp(r'\s+'), ' ');
  }
  
  // Tenter de remplacer un message temporaire par un message réel
  void _tryReplaceTemporaryMessage(int conversationId, String tempId, String originalContent) {
    if (_messages[conversationId] == null) return;
    
    final messages = _messages[conversationId]!;
    final normalizedContent = _normalizeContent(originalContent);
    
    // Chercher le message temporaire
    final tempIndex = messages.indexWhere((m) => m.tempId == tempId);
    if (tempIndex == -1) return;
    
    // Chercher un message réel récent avec le même contenu
    final now = DateTime.now();
    final recentRealMessage = messages.firstWhere(
      (m) => 
        !m.isTemporary && 
        _normalizeContent(m.content) == normalizedContent &&
        m.senderId == _currentUserId &&
        now.difference(m.createdAt).inMinutes < 5, // Créé dans les 5 dernières minutes
      orElse: () => Message(id: -1, content: '', conversationId: 0, createdAt: DateTime.now(), updatedAt: DateTime.now(), isRead: false),
    );
    
    if (recentRealMessage.id != -1) {
      // Remplacer le message temporaire
      messages.removeAt(tempIndex);
      _tempMessageMapping.remove(tempId);
      notifyListeners();
      print('[MessageProvider] Replaced temporary message $tempId with real message ${recentRealMessage.id}');
    }
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

      // Sauvegarder les messages temporaires existants
      List<Message> tempMessages = [];
      if (_messages.containsKey(conversationId)) {
        tempMessages = _messages[conversationId]!
            .where((m) => m.isTemporary)
            .toList();
      }

      // Charger les messages depuis l'API
      if (!_messages.containsKey(conversationId)) {
        _messages[conversationId] = [];
      }

      final List<Message> loadedMessages = await _messageService.getConversationMessages(conversationId);
      
      // Combiner les messages réels avec les temporaires
      final allMessages = <Message>[];
      allMessages.addAll(loadedMessages);
      allMessages.addAll(tempMessages);
      
      // Trier par date de création (du plus ancien au plus récent)
      allMessages.sort((a, b) => a.createdAt.compareTo(b.createdAt));
      _messages[conversationId] = allMessages;
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
          
          print('[MessageProvider] Received new message: ${message.id}, content: "${message.content}", sender: ${message.senderId}');
          
          // Vérifier que le message n'existe pas déjà (par ID réel)
          final existingIndex = _messages[conversationId]!.indexWhere((m) => 
            !m.isTemporary && m.id == message.id
          );
          
          if (existingIndex != -1) {
            print('[MessageProvider] Message ${message.id} already exists, ignoring');
            return; // Message déjà présent
          }
          
          // Si c'est notre propre message, chercher et remplacer le temporaire
          if (message.senderId == _currentUserId) {
            final normalizedContent = _normalizeContent(message.content);
            
            // Chercher le message temporaire correspondant
            final tempIndex = _messages[conversationId]!.indexWhere((m) => 
              m.isTemporary && 
              _normalizeContent(m.content) == normalizedContent &&
              m.senderId == message.senderId
            );
            
            if (tempIndex != -1) {
              // Remplacer le message temporaire par le message réel
              final tempId = _messages[conversationId]![tempIndex].tempId;
              _messages[conversationId]![tempIndex] = message;
              _tempMessageMapping.remove(tempId);
              
              print('[MessageProvider] Replaced temporary message $tempId with real message ${message.id}');
              
              // Trier les messages par date
              _messages[conversationId]!.sort((a, b) => a.createdAt.compareTo(b.createdAt));
              notifyListeners();
              return; // Ne pas ajouter en double
            }
          }
          
          // Vérification finale de déduplication par contenu récent
          final normalizedContent = _normalizeContent(message.content);
          final recentDuplicate = _messages[conversationId]!.any((m) =>
            !m.isTemporary && 
            m.senderId == message.senderId &&
            _normalizeContent(m.content) == normalizedContent &&
            DateTime.now().difference(m.createdAt).inMinutes < 2 // Dans les 2 dernières minutes
          );
          
          if (recentDuplicate) {
            print('[MessageProvider] Recent duplicate message detected, ignoring');
            return;
          }
          
          // Ajouter le nouveau message
          _messages[conversationId]!.add(message);
          _messages[conversationId]!.sort((a, b) => a.createdAt.compareTo(b.createdAt));
          notifyListeners();
          
          print('[MessageProvider] Added new message ${message.id}');
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
          
          // Mettre à jour le unreadCount de la conversation
          final convIndex = _conversations.indexWhere((c) => c.id == convId);
          if (convIndex != -1) {
            final conv = _conversations[convIndex];
            _conversations[convIndex] = Conversation(
              id: conv.id,
              type: conv.type,
              relatedId: conv.relatedId,
              createdAt: conv.createdAt,
              updatedAt: conv.updatedAt,
              participants: conv.participants,
              lastMessage: conv.lastMessage,
              unreadCount: 0,  // Réinitialiser le compteur à 0
              plantInfo: conv.plantInfo,
              plantCareInfo: conv.plantCareInfo,
            );
            updated = true;
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
      // Charger l'ID utilisateur si pas encore fait
      if (_currentUserId == null) {
        await _loadCurrentUserId();
      }
      
      if (_currentUserId == null) {
        throw Exception('User ID not available');
      }
      
      // Générer un ID temporaire unique
      final tempId = _generateTempId();
      final normalizedContent = _normalizeContent(content);
      
      // Vérifier qu'il n'y a pas déjà un message temporaire avec le même contenu
      final existingTemp = _messages[conversationId]?.any((m) => 
        m.isTemporary && 
        _normalizeContent(m.content) == normalizedContent &&
        m.senderId == _currentUserId
      ) ?? false;
      
      if (existingTemp) {
        print('[MessageProvider] Duplicate temporary message detected, ignoring');
        return;
      }
      
      // Créer un message temporaire
      final tempMessage = Message(
        id: 0, // ID temporaire sera ignoré
        content: content,
        senderId: _currentUserId!,
        conversationId: conversationId,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        isRead: false,
        tempId: tempId,
      );
      
      // Ajouter le message localement immédiatement (optimistic UI)
      if (_messages[conversationId] == null) {
        _messages[conversationId] = [];
      }
      _messages[conversationId]!.add(tempMessage);
      _messages[conversationId]!.sort((a, b) => a.createdAt.compareTo(b.createdAt));
      
      // Stocker le mapping pour référence
      _tempMessageMapping[tempId] = conversationId;
      notifyListeners();
      
      print('[MessageProvider] Added temporary message: $tempId');
      
      // Si WebSocket connecté, envoyer via WebSocket
      if (_webSocketManager.isConnected) {
        _webSocketManager.sendMessage({
          'type': 'message',
          'content': content,
          'conversation_id': conversationId,
          'temp_id': tempId, // Envoyer l'ID temporaire pour référence
        });
      } else {
        // Sinon, utiliser l'API REST comme fallback
        print('[MessageProvider] WebSocket not connected, using REST API');
        await _messageService.sendMessageViaAPI(conversationId, content);
        
        // Recharger les messages pour obtenir le message créé
        // loadMessages préservera automatiquement les messages temporaires
        await loadMessages(conversationId);
        
        // Tenter de remplacer le message temporaire par le vrai
        _tryReplaceTemporaryMessage(conversationId, tempId, content);
      }
    } catch (e) {
      print('[MessageProvider] Error sending message: $e');
      _error = e.toString();
      
      // En cas d'erreur, retirer le message temporaire si présent
      if (_messages[conversationId] != null) {
        _messages[conversationId]!.removeWhere((m) => m.isTemporary);
        notifyListeners();
      }
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
      
      // Mise à jour locale immédiate du unreadCount
      final convIndex = _conversations.indexWhere((c) => c.id == conversationId);
      if (convIndex != -1) {
        final conv = _conversations[convIndex];
        if (conv.unreadCount > 0) {
          _conversations[convIndex] = Conversation(
            id: conv.id,
            type: conv.type,
            relatedId: conv.relatedId,
            createdAt: conv.createdAt,
            updatedAt: conv.updatedAt,
            participants: conv.participants,
            lastMessage: conv.lastMessage,
            unreadCount: 0,  // Réinitialiser immédiatement
            plantInfo: conv.plantInfo,
            plantCareInfo: conv.plantCareInfo,
          );
          notifyListeners();
        }
      }
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
    _tempMessageMapping.clear();
    _error = null;
    _isLoading = false;
    disconnectWebSocket();
    notifyListeners();
  }
  
  // Nettoyer les messages temporaires non confirmés après 60 secondes
  void _cleanupOldTempMessages() {
    final now = DateTime.now();
    bool hasChanges = false;
    List<String> toRemove = [];
    
    _messages.forEach((conversationId, messages) {
      final beforeCount = messages.length;
      final removedMessages = <Message>[];
      
      messages.removeWhere((m) {
        if (m.isTemporary && now.difference(m.createdAt).inSeconds > 60) {
          removedMessages.add(m);
          return true;
        }
        return false;
      });
      
      if (messages.length != beforeCount) {
        hasChanges = true;
        // Nettoyer le mapping
        for (final removed in removedMessages) {
          if (removed.tempId != null) {
            toRemove.add(removed.tempId!);
          }
        }
      }
    });
    
    // Nettoyer les mappings
    for (final tempId in toRemove) {
      _tempMessageMapping.remove(tempId);
    }
    
    if (hasChanges) {
      print('[MessageProvider] Cleaned up ${toRemove.length} old temporary messages');
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _closeWebSocketSubscriptions();
    _webSocketManager.dispose();
    _messageService.dispose();
    super.dispose();
  }
} 
