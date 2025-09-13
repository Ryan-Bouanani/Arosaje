import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';

class AdaptiveImage extends StatelessWidget {
  final String? imageUrl;
  final String? imageBase64;
  final BoxFit fit;
  final double? width;
  final double? height;
  final Widget? errorWidget;

  const AdaptiveImage({
    super.key,
    this.imageUrl,
    this.imageBase64,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.errorWidget,
  });

  @override
  Widget build(BuildContext context) {
    // Priorité au Base64 (nouveau système)
    if (imageBase64 != null && imageBase64!.isNotEmpty) {
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
        print('Erreur décodage Base64: $e');
        return _buildErrorWidget();
      }
    }
    
    // Fallback vers l'URL (ancien système)
    if (imageUrl != null && imageUrl!.isNotEmpty) {
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