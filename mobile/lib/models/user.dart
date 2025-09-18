class User {
  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String? telephone;
  final String? location;
  final String role;
  final bool isVerified;

  User({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.telephone,
    this.location,
    required this.role,
    required this.isVerified,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      telephone: json['telephone'],
      location: json['location'],
      role: json['role'],
      isVerified: json['is_verified'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'telephone': telephone,
      'location': location,
      'role': role,
      'is_verified': isVerified,
    };
  }
  
  // Helper method pour obtenir le nom complet
  String get fullName => '$firstName $lastName';
  
  // Alias pour compatibilité
  String get username => fullName;
} 
