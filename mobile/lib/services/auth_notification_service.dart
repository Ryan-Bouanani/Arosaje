import 'dart:async';

/// Service de notification global pour les changements d'authentification
/// Permet de notifier l'AuthWrapper quand l'utilisateur est déconnecté automatiquement
class AuthNotificationService {
  static final AuthNotificationService _instance = AuthNotificationService._internal();
  factory AuthNotificationService() => _instance;
  AuthNotificationService._internal();

  // StreamController pour les notifications d'authentification
  final StreamController<AuthState> _authStateController = StreamController<AuthState>.broadcast();

  /// Stream pour écouter les changements d'authentification
  Stream<AuthState> get authStateStream => _authStateController.stream;

  /// État actuel de l'authentification
  AuthState _currentState = AuthState.unknown;
  AuthState get currentState => _currentState;

  /// Notifie que l'utilisateur s'est connecté avec succès
  void notifyLoggedIn() {
    _currentState = AuthState.authenticated;
    _authStateController.add(AuthState.authenticated);
  }

  /// Notifie que l'utilisateur s'est déconnecté (manuellement ou automatiquement)
  void notifyLoggedOut({bool automatic = false}) {
    _currentState = automatic ? AuthState.expiredLogout : AuthState.manualLogout;
    _authStateController.add(_currentState);
  }

  /// Notifie qu'il y a eu une erreur d'authentification (token expiré)
  void notifyAuthError() {
    _currentState = AuthState.authError;
    _authStateController.add(AuthState.authError);
  }

  /// Ferme les streams (à appeler lors de la destruction de l'app)
  void dispose() {
    _authStateController.close();
  }
}

/// États possibles de l'authentification
enum AuthState {
  unknown,        // État initial, non déterminé
  authenticated,  // Utilisateur authentifié
  manualLogout,   // Déconnexion manuelle
  expiredLogout,  // Déconnexion automatique (token expiré)
  authError,      // Erreur d'authentification
}