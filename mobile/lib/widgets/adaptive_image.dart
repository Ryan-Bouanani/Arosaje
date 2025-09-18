import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';

class AdaptiveImage extends StatelessWidget {
  final String? imageBase64;
  final BoxFit fit;
  final double? width;
  final double? height;
  final Widget? errorWidget;

  const AdaptiveImage({
    super.key,
    this.imageBase64,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.errorWidget,
  });

  @override
  Widget build(BuildContext context) {
    if (imageBase64 != null && imageBase64!.isNotEmpty) {
      return _buildFromBase64();
    }
    return _buildErrorWidget();
  }

  Widget _buildFromBase64() {
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