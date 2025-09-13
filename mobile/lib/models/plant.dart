class Plant {
  final int id;
  final String nom;
  final String? espece;
  final String? photo;
  final String? photoBase64;
  final int? ownerId;

  Plant({
    required this.id,
    required this.nom,
    this.espece,
    this.photo,
    this.photoBase64,
    this.ownerId,
  });

  factory Plant.fromJson(Map<String, dynamic> json) {
    return Plant(
      id: json['id'],
      nom: json['nom'],
      espece: json['espece'],
      photo: json['photo'],
      photoBase64: json['photo_base64'],
      ownerId: json['owner_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nom': nom,
      'espece': espece,
      'photo': photo,
      'photo_base64': photoBase64,
      'owner_id': ownerId,
    };
  }
} 
