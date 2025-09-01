# Flutter Installation Script for A'rosa-je
Write-Host "=== Installing Flutter SDK ===" -ForegroundColor Green
Write-Host ""

$flutterUrl = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.24.5-stable.zip"
$zipPath = "$env:TEMP\flutter.zip"
$extractPath = "C:\"

# Check if Flutter already exists
if (Test-Path "C:\flutter\bin\flutter.bat") {
    Write-Host "Flutter is already installed at C:\flutter" -ForegroundColor Yellow
    $response = Read-Host "Do you want to reinstall? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Using existing Flutter installation"
        exit 0
    }
}

Write-Host "Downloading Flutter SDK (this may take a few minutes)..." -ForegroundColor Cyan
try {
    # Download Flutter
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $flutterUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
    
    # Extract Flutter
    Write-Host "Extracting Flutter SDK to C:\flutter..." -ForegroundColor Cyan
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
    Write-Host "Extraction complete!" -ForegroundColor Green
    
    # Add to PATH
    Write-Host "Adding Flutter to PATH..." -ForegroundColor Cyan
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*C:\flutter\bin*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\flutter\bin", "User")
        Write-Host "Flutter added to PATH!" -ForegroundColor Green
    }
    
    # Clean up
    Remove-Item $zipPath -Force
    
    Write-Host ""
    Write-Host "Flutter installation complete!" -ForegroundColor Green
    Write-Host "Please restart your terminal or VS Code to use Flutter" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To launch the app, run:" -ForegroundColor Cyan
    Write-Host "  cd mobile" -ForegroundColor White
    Write-Host "  C:\flutter\bin\flutter run -d emulator-5554" -ForegroundColor White
    
} catch {
    Write-Host "Error installing Flutter: $_" -ForegroundColor Red
    exit 1
}