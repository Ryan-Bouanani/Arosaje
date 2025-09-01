import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:mobile/models/conversation.dart';
import 'package:mobile/models/message.dart';
import 'package:mobile/services/api_service.dart';

class MessageService {
  final ApiService _apiService;
  WebSocketChannel? _channel;
  final _messageController = StreamController<Message>.broadcast();
  final _typingController = StreamController<Map<String, dynamic>>.broadcast();
  final _readController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<Message> get onMessage => _messageController.stream;
  Stream<Map<String, dynamic>> get onTyping => _typingController.stream;
  Stream<Map<String, dynamic>> get onRead => _readController.stream;

  MessageService(this._apiService);

  // Créer une conversation avec un botaniste
  Future<Map<String, dynamic>> createBotanistConversation(int plantId) async {
    try {
      final response = await _apiService.post(
        '/messages/conversations/botanist?plant_id=$plantId',
        {},
      );
      return response;
    } catch (e) {
      throw Exception('Erreur lors de la création de la conversation avec le botaniste: $e');
    }
  }

  // Envoyer un message via l'API REST
  Future<void> sendMessageViaAPI(int conversationId, String content) async {
    try {
      final response = await _apiService.post(
        '/messages/$conversationId',
        {
          'content': content,
          'conversation_id': conversationId
        },
      );
      print('Message sent via API: $response');
    } catch (e) {
      throw Exception('Erreur lors de l\'envoi du message: $e');
    }
  }

  // Méthodes API REST
  Future<List<Conversation>> getUserConversations({
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final response = await _apiService.get(
        '/messages/conversations',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      
      if (response is List) {
        final conversations = response
            .map((json) {
              try {
                return Conversation.fromJson(json as Map<String, dynamic>);
              } catch (e) {
                return null;
              }
            })
            .where((conv) => conv != null)
            .cast<Conversation>()
            .toList();
        
        return conversations;
      } else if (response is Map<String, dynamic> && response.containsKey('data')) {
        return (response['data'] as List)
            .map((json) => Conversation.fromJson(json))
            .toList();
      } else {
        return [];
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Message>> getConversationMessages(
    int conversationId, {
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final response = await _apiService.get(
        '/messages/conversations/$conversationId/messages',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      
      if (response is List) {
        final messages = response
            .map((json) {
              try {
                return Message.fromJson(json as Map<String, dynamic>);
              } catch (e) {
                return null;
              }
            })
            .where((msg) => msg != null)
            .cast<Message>()
            .toList();
        
        return messages;
      } else if (response is Map<String, dynamic> && response.containsKey('data')) {
        return (response['data'] as List)
            .map((json) => Message.fromJson(json))
            .toList();
      } else {
        return [];
      }
    } catch (e) {
      rethrow;
    }
  }

  // WebSocket
  Future<void> connectToConversation(int conversationId) async {
    try {
      final token = await _apiService.getToken();
      if (token == null) {
        throw Exception('No authentication token available');
      }
      
      // Passer le token comme paramètre de query dans l'URL
      final String apiUrl = dotenv.env['FLUTTER_API_URL'] ?? '/api';
      final wsUrl = Uri.parse('${apiUrl.replaceFirst("http", "ws")}/ws/$conversationId?token=$token');
      
      _channel = WebSocketChannel.connect(wsUrl);

      _channel!.stream.listen(
        (message) {
          final data = jsonDecode(message);
          switch (data['type']) {
            case 'new_message':
              _messageController.add(Message.fromJson(data['message']));
              break;
            case 'typing_status':
              _typingController.add(data);
              break;
            case 'messages_read':
              _readController.add(data);
              break;
          }
        },
        onError: (error) {
          _reconnectToConversation(conversationId);
        },
        onDone: () {
          _reconnectToConversation(conversationId);
        },
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _reconnectToConversation(int conversationId) async {
    await Future.delayed(const Duration(seconds: 2));
    try {
      await connectToConversation(conversationId);
    } catch (e) {
      // Reconnexion échouée, on peut réessayer plus tard
    }
  }

  // Renommage de l'ancienne méthode pour éviter les conflits
  Future<void> reconnectToConversation(int conversationId) async {
    await _reconnectToConversation(conversationId);
  }

  void sendMessage(String content, {int? conversationId}) {
    if (_channel != null && conversationId != null) {
      _channel!.sink.add(jsonEncode({
        'type': 'message',
        'content': content,
        'conversation_id': conversationId,
      }));
    }
  }

  void sendTypingStatus(bool isTyping) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode({
        'type': 'typing',
        'is_typing': isTyping,
      }));
    }
  }

  void markMessagesAsRead() {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode({
        'type': 'read',
      }));
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }

  void dispose() {
    disconnect();
    _messageController.close();
    _typingController.close();
    _readController.close();
  }
} 