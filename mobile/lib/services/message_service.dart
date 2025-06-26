import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
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

  // Méthodes API REST
  Future<List<Conversation>> getUserConversations({
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      print('Fetching user conversations...');
      final response = await _apiService.get(
        '/messages/conversations',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      
      print('API Response type: ${response.runtimeType}');
      print('API Response: $response');
      
      if (response is List) {
        print('Processing ${response.length} conversations');
        final conversations = response
            .map((json) {
              try {
                return Conversation.fromJson(json as Map<String, dynamic>);
              } catch (e) {
                print('Error parsing conversation: $e');
                print('Conversation data: $json');
                return null;
              }
            })
            .where((conv) => conv != null)
            .cast<Conversation>()
            .toList();
        
        print('Successfully parsed ${conversations.length} conversations');
        return conversations;
      } else if (response is Map<String, dynamic> && response.containsKey('data')) {
        return (response['data'] as List)
            .map((json) => Conversation.fromJson(json))
            .toList();
      } else {
        print('Unexpected response format: $response');
        return [];
      }
    } catch (e) {
      print('Error in getUserConversations: $e');
      rethrow;
    }
  }

  Future<List<Message>> getConversationMessages(
    int conversationId, {
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      print('Fetching messages for conversation $conversationId');
      final response = await _apiService.get(
        '/messages/conversations/$conversationId/messages',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      
      print('Messages response type: ${response.runtimeType}');
      print('Messages response: $response');
      
      if (response is List) {
        final messages = response
            .map((json) {
              try {
                return Message.fromJson(json as Map<String, dynamic>);
              } catch (e) {
                print('Error parsing message: $e');
                print('Message data: $json');
                return null;
              }
            })
            .where((msg) => msg != null)
            .cast<Message>()
            .toList();
        
        print('Successfully parsed ${messages.length} messages');
        return messages;
      } else if (response is Map<String, dynamic> && response.containsKey('data')) {
        return (response['data'] as List)
            .map((json) => Message.fromJson(json))
            .toList();
      } else {
        print('Unexpected messages response format: $response');
        return [];
      }
    } catch (e) {
      print('Error in getConversationMessages: $e');
      rethrow;
    }
  }

  // WebSocket
  Future<void> connectToConversation(int conversationId) async {
    final token = await _apiService.getToken();
    final wsUrl = Uri.parse('${ApiService.baseUrl.replaceFirst("http", "ws")}/ws/$conversationId');
    
    _channel = WebSocketChannel.connect(
      wsUrl,
      protocols: ['Bearer $token'],
    );

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
        print('WebSocket error: $error');
        reconnectToConversation(conversationId);
      },
      onDone: () {
        print('WebSocket connection closed');
        reconnectToConversation(conversationId);
      },
    );
  }

  Future<void> reconnectToConversation(int conversationId) async {
    await Future.delayed(const Duration(seconds: 2));
    try {
      await connectToConversation(conversationId);
    } catch (e) {
      print('Reconnection failed: $e');
    }
  }

  void sendMessage(String content) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode({
        'type': 'message',
        'content': content,
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