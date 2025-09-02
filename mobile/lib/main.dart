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

Future<void> main() async {
  try {
    WidgetsFlutterBinding.ensureInitialized();
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
    await dotenv.load(fileName: "assets/.env.mobile");
    runApp(const MyApp());
  } catch (e) {
    print('Erreur lors de l\'initialisation: $e');
    runApp(const MyApp()); // Démarrer l'app même en cas d'erreur
  }
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
        title: 'A\'rosa-je',
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
