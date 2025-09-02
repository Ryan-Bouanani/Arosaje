import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AddressAutocompleteField extends StatefulWidget {
  final Function(String address, double? lat, double? lng) onAddressSelected;
  final String? initialValue;
  final String? hintText;
  final String? labelText;
  final InputDecoration? decoration;

  const AddressAutocompleteField({
    super.key,
    required this.onAddressSelected,
    this.initialValue,
    this.hintText,
    this.labelText,
    this.decoration,
  });

  @override
  State<AddressAutocompleteField> createState() => _AddressAutocompleteFieldState();
}

class _AddressAutocompleteFieldState extends State<AddressAutocompleteField> {
  final TextEditingController _addressController = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  
  List<Map<String, dynamic>> _suggestions = [];
  bool _showSuggestions = false;
  bool _isLoading = false;
  String? _errorMessage;
  Timer? _debounceTimer;
  http.Client? _httpClient;
  bool _isSelecting = false;
  
  // URL de l'API backend
  final String _baseUrl = dotenv.env['FLUTTER_API_URL'] ?? 'http://localhost:8000';

  @override
  void initState() {
    super.initState();
    _httpClient = http.Client();
    
    if (widget.initialValue != null) {
      _addressController.text = widget.initialValue!;
    }
    
    _addressController.addListener(_onTextChanged);
    
    // Gestion du focus sans fermer immédiatement les suggestions
    _focusNode.addListener(() {
      if (_focusNode.hasFocus) {
        // Quand le champ reçoit le focus, réafficher les suggestions si on en a
        if (_suggestions.isNotEmpty && _addressController.text.isNotEmpty) {
          setState(() => _showSuggestions = true);
        }
      } else {
        // Délai avant de fermer pour permettre les clics sur les suggestions
        Timer(const Duration(milliseconds: 150), () {
          if (mounted) {
            setState(() => _showSuggestions = false);
          }
        });
      }
    });
  }

  void _onTextChanged() {
    // Si on est en train de sélectionner, ignorer les changements
    if (_isSelecting) {
      _isSelecting = false;
      return;
    }
    
    final query = _addressController.text.trim();
    
    // Nettoyer les erreurs et suggestions si le champ est vide
    if (query.isEmpty) {
      _cancelCurrentRequest();
      setState(() {
        _suggestions = [];
        _showSuggestions = false;
        _errorMessage = null;
        _isLoading = false;
      });
      return;
    }

    // Débounce pour éviter trop d'appels API
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 300), () {
      _searchPlaces(query);
    });
  }

  void _cancelCurrentRequest() {
    _debounceTimer?.cancel();
    _httpClient?.close();
    _httpClient = http.Client();
  }

  Future<void> _searchPlaces(String query) async {
    if (!mounted) return;
    
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    
    try {
      final url = Uri.parse('$_baseUrl/geocoding/autocomplete')
          .replace(queryParameters: {
        'query': query,
        'country': 'fr',
      });
      
      final response = await _httpClient!.get(url).timeout(
        const Duration(seconds: 5),
        onTimeout: () => throw TimeoutException('Délai d\'attente dépassé'),
      );
      
      if (!mounted) return;
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final suggestions = data['suggestions'] as List<dynamic>? ?? [];
        
        setState(() {
          _suggestions = suggestions.cast<Map<String, dynamic>>();
          _showSuggestions = suggestions.isNotEmpty;
          _isLoading = false;
          _errorMessage = null;
        });
        
      } else {
        setState(() {
          _suggestions = [];
          _showSuggestions = false;
          _isLoading = false;
          _errorMessage = 'Erreur de connexion (${response.statusCode})';
        });
      }
      
    } catch (e) {
      if (!mounted) return;
      
      setState(() {
        _suggestions = [];
        _showSuggestions = false;
        _isLoading = false;
        _errorMessage = e is TimeoutException 
          ? 'Délai d\'attente dépassé' 
          : 'Erreur de connexion';
      });
    }
  }

  void _selectSuggestion(Map<String, dynamic> suggestion) {
    final address = suggestion['description'] as String? ?? '';
    
    // Annuler toute recherche en cours
    _cancelCurrentRequest();
    
    // Marquer qu'on est en train de sélectionner pour ignorer le prochain onTextChanged
    _isSelecting = true;
    
    // Mettre à jour le champ et fermer les suggestions
    setState(() {
      _addressController.text = address;
      _showSuggestions = false;
      _suggestions = [];
      _isLoading = false;
      _errorMessage = null;
    });
    
    // Notifier la sélection
    widget.onAddressSelected(address, null, null);
    
    // Retirer le focus pour finaliser la sélection
    _focusNode.unfocus();
  }

  void _clearField() {
    _cancelCurrentRequest();
    _isSelecting = true; // Empêcher la recherche lors du clear
    _addressController.clear();
    setState(() {
      _suggestions = [];
      _showSuggestions = false;
      _isLoading = false;
      _errorMessage = null;
    });
  }


  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
          TextFormField(
            controller: _addressController,
            focusNode: _focusNode,
            decoration: (widget.decoration ?? InputDecoration(
              hintText: widget.hintText ?? "Commencez à taper une adresse...",
              labelText: widget.labelText ?? "Localisation",
              filled: true,
              fillColor: Colors.green.withOpacity(0.1),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide(color: Colors.green[700]!, width: 2),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: const BorderSide(color: Colors.red, width: 2),
              ),
              prefixIcon: Icon(Icons.location_on, color: Colors.green[700]),
            )).copyWith(
              suffixIcon: _buildSuffixIcon(),
              helperText: _errorMessage == null 
                ? "Sélectionnez une suggestion ou tapez librement" 
                : null,
              helperStyle: TextStyle(
                fontSize: 11,
                color: Colors.grey[600],
              ),
              errorText: _errorMessage,
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'L\'adresse est requise';
              }
              return null;
            },
          ),
          
          // Suggestions directement dans la colonne
          if (_showSuggestions && _suggestions.isNotEmpty)
            Container(
              constraints: const BoxConstraints(maxHeight: 200),
              margin: const EdgeInsets.only(top: 4),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey.shade300),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    spreadRadius: 1,
                    blurRadius: 5,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: ListView.separated(
                shrinkWrap: true,
                padding: EdgeInsets.zero,
                itemCount: _suggestions.length,
                separatorBuilder: (context, index) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final suggestion = _suggestions[index];
                  final mainText = suggestion['main_text'] as String? ?? '';
                  final secondaryText = suggestion['secondary_text'] as String? ?? '';
                  
                  return InkWell(
                    onTap: () => _selectSuggestion(suggestion),
                    child: ListTile(
                      dense: true,
                      leading: Icon(Icons.location_on, 
                        color: Colors.green[700], 
                        size: 20
                      ),
                      title: Text(
                        mainText,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      subtitle: secondaryText.isNotEmpty 
                        ? Text(
                            secondaryText,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ) 
                        : null,
                    ),
                  );
                },
              ),
            ),
        ],
    );
  }

  Widget _buildSuffixIcon() {
    if (_isLoading) {
      return const Padding(
        padding: EdgeInsets.all(12.0),
        child: SizedBox(
          width: 20,
          height: 20,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }
    
    if (_addressController.text.isNotEmpty) {
      return IconButton(
        icon: const Icon(Icons.clear),
        onPressed: _clearField,
      );
    }
    
    return const SizedBox.shrink();
  }

  @override
  void dispose() {
    _cancelCurrentRequest();
    _httpClient?.close();
    _addressController.dispose();
    _focusNode.dispose();
    super.dispose();
  }
}
