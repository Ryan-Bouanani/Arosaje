class Plant {
  final int id;
  final String name;
  final String? species;
  final String? photo;
  final String? photoBase64;
  final int? ownerId;

  Plant({
    required this.id,
    required this.name,
    this.species,
    this.photo,
    this.photoBase64,
    this.ownerId,
  });

  factory Plant.fromJson(Map<String, dynamic> json) {
    return Plant(
      id: json['id'],
      name: json['name'] ?? '',
      species: json['species'],
      photo: json['photo'],
      photoBase64: json['photo_base64'],
      ownerId: json['owner_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'species': species,
      'photo': photo,
      'photo_base64': photoBase64,
      'owner_id': ownerId,
    };
  }
} 
