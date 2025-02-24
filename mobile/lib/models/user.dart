class User {
  final int id;
  final String email;
  final String nom;
  final String prenom;
  final String? telephone;
  final String? localisation;
  final String role;
  final bool isVerified;

  User({
    required this.id,
    required this.email,
    required this.nom,
    required this.prenom,
    this.telephone,
    this.localisation,
    required this.role,
    required this.isVerified,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      nom: json['nom'],
      prenom: json['prenom'],
      telephone: json['telephone'],
      localisation: json['localisation'],
      role: json['role'],
      isVerified: json['is_verified'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'nom': nom,
      'prenom': prenom,
      'telephone': telephone,
      'localisation': localisation,
      'role': role,
      'is_verified': isVerified,
    };
  }
} 