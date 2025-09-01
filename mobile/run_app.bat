@echo off
echo === Launching A'rosa-je Mobile App ===
echo.

REM Check if Flutter exists
if exist "C:\flutter\bin\flutter.bat" (
    echo Flutter found at C:\flutter
    set FLUTTER_PATH=C:\flutter\bin\flutter.bat
) else if exist "%USERPROFILE%\flutter\bin\flutter.bat" (
    echo Flutter found at %USERPROFILE%\flutter
    set FLUTTER_PATH=%USERPROFILE%\flutter\bin\flutter.bat
) else (
    echo ERROR: Flutter not found!
    echo Please install Flutter first
    pause
    exit /b 1
)

echo.
echo Running Flutter app on emulator...
echo.

REM Run the app
"%FLUTTER_PATH%" run -d emulator-5554

pause