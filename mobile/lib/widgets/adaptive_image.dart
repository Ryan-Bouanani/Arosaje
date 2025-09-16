import 'dart:convert';
import 'dart:typed_data';
import 'dart:developer' as developer;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class AdaptiveImage extends StatelessWidget {
  final String? imageUrl;
  final String? imageBase64;
  final BoxFit fit;
  final double? width;
  final double? height;
  final Widget? errorWidget;
  final int? plantId; // Pour utiliser le proxy des images de plantes
  final int? reportId; // Pour utiliser le proxy des images de rapports

  const AdaptiveImage({
    super.key,
    this.imageUrl,
    this.imageBase64,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.errorWidget,
    this.plantId,
    this.reportId,
  });

  @override
  Widget build(BuildContext context) {
    // Sur Flutter Web, TOUJOURS utiliser l'endpoint API pour servir les images si plantId disponible
    if (kIsWeb && plantId != null) {
      const String baseUrl = "https://arosaje-backend-t2x7.onrender.com"; // API Render
      final String proxyUrl = "$baseUrl/plants/$plantId/image?v=${DateTime.now().millisecondsSinceEpoch}";

      return Image.network(
        proxyUrl,
        fit: fit,
        width: width,
        height: height,
        errorBuilder: (context, error, stackTrace) {
          return _fallbackToBase64();
        },
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) {
            return child;
          }
          return const CircularProgressIndicator();
        },
      );
    }

    // Sur Flutter Web, utiliser Base64 pour les rapports (car l'endpoint nécessite une authentification)
    if (kIsWeb && reportId != null) {
      return _fallbackToBase64();
    }

    // Priorité au Base64 (système standard pour mobile ou fallback)
    if (imageBase64 != null && imageBase64!.isNotEmpty) {
      return _fallbackToBase64();
    }
    
    // Fallback vers l'URL (ancien système) - mais seulement si ce n'est pas une URL assets/ éphémère
    if (imageUrl != null && imageUrl!.isNotEmpty && !imageUrl!.contains('assets/persisted_img/')) {
      return Image.network(
        imageUrl!,
        fit: fit,
        width: width,
        height: height,
        errorBuilder: (context, error, stackTrace) {
          return _buildErrorWidget();
        },
      );
    }
    
    return _buildErrorWidget();
  }

  Widget _fallbackToBase64() {
    try {
      // Extraire les données Base64 du data URL
      String base64Data = imageBase64!;
      if (base64Data.startsWith('data:')) {
        base64Data = base64Data.split(',')[1];
      }

      final Uint8List imageBytes = base64Decode(base64Data);

      return Image.memory(
        imageBytes,
        fit: fit,
        width: width,
        height: height,
        errorBuilder: (context, error, stackTrace) {
          return _buildErrorWidget();
        },
      );
    } catch (e) {
      return _buildErrorWidget();
    }
  }

  Widget _buildErrorWidget() {
    return errorWidget ?? Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Icon(
        Icons.image_not_supported,
        color: Colors.grey,
        size: 40,
      ),
    );
  }
}