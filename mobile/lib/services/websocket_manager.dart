import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

enum ConnectionState {
  disconnected,
  connecting,
  connected,
  disconnecting,
  error
}

class WebSocketManager {
  WebSocketChannel? _channel;
  ConnectionState _state = ConnectionState.disconnected;
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  
  // Configuration de reconnexion
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 5;
  static const List<int> reconnectDelays = [2, 4, 8, 16, 32]; // Backoff exponentiel
  
  // Configuration heartbeat
  static const Duration heartbeatInterval = Duration(seconds: 30);
  static const Duration heartbeatTimeout = Duration(seconds: 60);
  DateTime? _lastPong;
  
  // Callbacks
  final StreamController<dynamic> _messageController = StreamController.broadcast();
  final StreamController<ConnectionState> _stateController = StreamController.broadcast();
  final StreamController<String> _errorController = StreamController.broadcast();
  
  // Getters
  Stream<dynamic> get onMessage => _messageController.stream;
  Stream<ConnectionState> get onStateChange => _stateController.stream;
  Stream<String> get onError => _errorController.stream;
  ConnectionState get state => _state;
  bool get isConnected => _state == ConnectionState.connected;
  
  // Données de connexion
  String? _token;
  int? _conversationId;
  bool _shouldReconnect = true;
  bool _isDisposed = false;
  
  Future<void> connect({
    required String token,
    required int conversationId,
  }) async {
    // Connect called
    
    // Éviter les connexions multiples
    if (_state == ConnectionState.connecting || _state == ConnectionState.connected) {
      // Already connected
      return;
    }
    
    _token = token;
    _conversationId = conversationId;
    _shouldReconnect = true;
    
    await _doConnect();
  }
  
  Future<void> _doConnect() async {
    if (_isDisposed) return;
    
    try {
      _setState(ConnectionState.connecting);
      // Attempting connection
      
      final String apiUrl = dotenv.env['FLUTTER_API_URL'] ?? '/api';
      final wsUrl = Uri.parse('${apiUrl.replaceFirst("http", "ws")}/ws/$_conversationId?token=$_token');
      
      // WebSocket URL: $wsUrl
      
      _channel = WebSocketChannel.connect(wsUrl);
      
      // Écouter les messages
      _channel!.stream.listen(
        (message) {
          _handleMessage(message);
          _lastPong = DateTime.now();
        },
        onError: (error) {
          // WebSocket error
          _handleError(error);
        },
        onDone: () {
          // WebSocket closed
          _handleClose();
        },
        cancelOnError: false,
      );
      
      // Attendre un court instant pour vérifier la connexion
      await Future.delayed(Duration(milliseconds: 500));
      
      if (_channel?.closeCode == null) {
        // Connexion réussie
        _setState(ConnectionState.connected);
        _reconnectAttempts = 0;
        _startHeartbeat();
        // Connected successfully
      } else {
        throw Exception('Connection failed with code: ${_channel?.closeCode}');
      }
      
    } catch (e) {
      print('[WebSocketManager ERROR] Connection failed: $e');
      _setState(ConnectionState.error);
      _errorController.add('Connection failed: $e');
      _scheduleReconnect();
    }
  }
  
  void _handleMessage(dynamic message) {
    try {
      final data = jsonDecode(message);
      // Message received: ${data['type']}
      
      // Gérer le ping/pong pour le heartbeat
      if (data['type'] == 'pong') {
        _lastPong = DateTime.now();
        return;
      }
      
      _messageController.add(data);
    } catch (e) {
      // Error parsing message
    }
  }
  
  void _handleError(dynamic error) {
    // Error occurred
    _setState(ConnectionState.error);
    _errorController.add(error.toString());
    
    // Déterminer si on doit tenter une reconnexion
    if (_shouldReconnect && error.toString().contains('401')) {
      // Erreur d'authentification - ne pas reconnecter
      print('[WebSocketManager ERROR] Authentication failed - not reconnecting');
      _shouldReconnect = false;
      disconnect();
    } else if (_shouldReconnect) {
      _scheduleReconnect();
    }
  }
  
  void _handleClose() {
    // Connection closed
    _stopHeartbeat();
    
    if (_state != ConnectionState.disconnecting) {
      // Fermeture inattendue
      _setState(ConnectionState.disconnected);
      if (_shouldReconnect) {
        _scheduleReconnect();
      }
    } else {
      // Fermeture volontaire
      _setState(ConnectionState.disconnected);
    }
  }
  
  void _scheduleReconnect() {
    if (!_shouldReconnect || _isDisposed) return;
    
    if (_reconnectAttempts >= maxReconnectAttempts) {
      print('[WebSocketManager ERROR] Max reconnection attempts reached');
      _errorController.add('Unable to connect after $maxReconnectAttempts attempts');
      _shouldReconnect = false;
      return;
    }
    
    // Calculer le délai avec backoff exponentiel
    final delaySeconds = reconnectDelays[_reconnectAttempts.clamp(0, reconnectDelays.length - 1)];
    // Scheduling reconnect in $delaySeconds seconds
    
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(Duration(seconds: delaySeconds), () {
      if (_shouldReconnect && !_isDisposed) {
        _reconnectAttempts++;
        _doConnect();
      }
    });
  }
  
  void _startHeartbeat() {
    _stopHeartbeat();
    _lastPong = DateTime.now();
    
    _heartbeatTimer = Timer.periodic(heartbeatInterval, (timer) {
      if (_state != ConnectionState.connected || _channel == null) {
        _stopHeartbeat();
        return;
      }
      
      // Vérifier le timeout
      if (_lastPong != null) {
        final timeSinceLastPong = DateTime.now().difference(_lastPong!);
        if (timeSinceLastPong > heartbeatTimeout) {
          // Heartbeat timeout
          _handleClose();
          return;
        }
      }
      
      // Envoyer un ping
      try {
        sendMessage({'type': 'ping'});
      } catch (e) {
        // Failed to send ping
      }
    });
  }
  
  void _stopHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
  }
  
  void sendMessage(Map<String, dynamic> message) {
    if (_state != ConnectionState.connected || _channel == null) {
      // Cannot send - not connected
      throw Exception('WebSocket not connected');
    }
    
    try {
      _channel!.sink.add(jsonEncode(message));
      // Message sent
    } catch (e) {
      // Send failed
      throw e;
    }
  }
  
  Future<void> disconnect() async {
    // Disconnect called
    _shouldReconnect = false;
    _reconnectTimer?.cancel();
    _stopHeartbeat();
    
    if (_channel != null) {
      _setState(ConnectionState.disconnecting);
      await _channel!.sink.close();
      _channel = null;
    }
    
    _setState(ConnectionState.disconnected);
  }
  
  void _setState(ConnectionState newState) {
    if (_state != newState) {
      // State change: $_state -> $newState
      _state = newState;
      _stateController.add(newState);
    }
  }
  
  void dispose() {
    // Disposing
    _isDisposed = true;
    _shouldReconnect = false;
    disconnect();
    _messageController.close();
    _stateController.close();
    _errorController.close();
  }
}