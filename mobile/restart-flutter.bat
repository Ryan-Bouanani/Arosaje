@echo off
echo 🔄 Redémarrage Flutter Web complet...
echo.

echo 1️⃣ Nettoyage du projet...
flutter clean

echo.
echo 2️⃣ Récupération des dépendances...
flutter pub get

echo.
echo 3️⃣ Lancement de Flutter Web...
flutter run -d chrome --web-port=5000

pause