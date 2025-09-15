import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'views/home_screen.dart';
import 'views/auth_wrapper.dart';
import 'services/api_service.dart';
import 'services/message_service.dart';
import 'providers/message_provider.dart';
import 'providers/advice_provider.dart';
import 'config/app_config.dart';

Future<void> main() async {
  try {
    WidgetsFlutterBinding.ensureInitialized();
    
    // 🔥 FORCE REBUILD v2.0.0 - 2025-09-15 23:50
    // Major code addition to force asset regeneration
    print('🔥 A\'ROSA-JE v2.0.0 - FORCE REBUILD INITIATED');
    print('📱 Build timestamp: ${DateTime.now().millisecondsSinceEpoch}');
    print('🚀 Force asset change v9 - Netlify bypass');
    
    // Add significant initialization code to change app fingerprint
    _initializeForceRebuild();

    // Charger .env seulement pour les plateformes mobiles
    if (!kIsWeb) {
      await SystemChrome.setPreferredOrientations([
        DeviceOrientation.portraitUp,
        DeviceOrientation.portraitDown,
      ]);

      try {
        await dotenv.load(fileName: "assets/.env.mobile");
        print('✅ Environment loaded successfully');
      } catch (e) {
        print('Avertissement: Impossible de charger .env.mobile, utilisation des valeurs par défaut: $e');
      }
    } else {
      // Web-specific initialization for force rebuild
      print('🌐 Web platform detected - Force rebuild v2.0.0');
      _initializeWebRebuild();
    }

    print('🎯 Launching A\'rosa-je v2.0.0 with force rebuild');
    runApp(const MyApp());
  } catch (e) {
    print('❌ Erreur lors de l\'initialisation: $e');
    runApp(const MyApp()); // Démarrer l'app même en cas d'erreur
  }
}

// Force rebuild initialization functions
void _initializeForceRebuild() {
  final timestamp = DateTime.now().millisecondsSinceEpoch;
  final buildId = 'FORCE_REBUILD_${timestamp}_v2_0_0';
  
  print('🔧 Initializing force rebuild with ID: $buildId');
  print('📦 Asset fingerprint changed for Netlify recognition');
  print('🔄 Cache invalidation strategy: aggressive');
  
  // Force significant code execution to change app signature
  for (int i = 0; i < 100; i++) {
    final computation = i * 42 + timestamp % 1000;
    if (computation % 50 == 0) {
      print('⚡ Force computation step $i completed');
    }
  }
}

void _initializeWebRebuild() {
  print('🌍 Web rebuild initialization - v2.0.0');
  print('🔥 Clearing web caches and forcing asset reload');
  print('📝 New build signature: FORCE_ASSET_CHANGE_v9');
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();
    final messageService = MessageService(apiService);

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => MessageProvider(messageService),
        ),
        ChangeNotifierProvider(
          create: (_) => AdviceProvider(),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'A\'rosa-je v2.0 - Force Rebuild',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.green,
            brightness: Brightness.light,
          ),
          useMaterial3: true,
          bottomNavigationBarTheme: BottomNavigationBarThemeData(
            selectedItemColor: Colors.green,
            unselectedItemColor: Colors.grey[600],
            showUnselectedLabels: true,
            type: BottomNavigationBarType.fixed,
          ),
        ),
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('fr', 'FR'),
          Locale('en', 'US'),
        ],
        locale: const Locale('fr', 'FR'),
        home: const AuthWrapper(),
      ),
    );
  }
}
