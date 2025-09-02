class Plant {
  final int id;
  final String nom;
  final String? espece;
  final String? photo;
  final int? ownerId;

  Plant({
    required this.id,
    required this.nom,
    this.espece,
    this.photo,
    this.ownerId,
  });

  factory Plant.fromJson(Map<String, dynamic> json) {
    return Plant(
      id: json['id'],
      nom: json['nom'],
      espece: json['espece'],
      photo: json['photo'],
      ownerId: json['owner_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nom': nom,
      'espece': espece,
      'photo': photo,
      'owner_id': ownerId,
    };
  }
} 
