import 'package:mobile/models/message.dart';
import 'package:mobile/models/user.dart';

enum ConversationType {
  plantCare,
  botanicalAdvice;

  String toJson() => name;
  static ConversationType fromJson(String json) {
    // Gérer aussi les valeurs de l'API qui utilisent des underscores
    switch (json.toLowerCase()) {
      case 'plant_care':
        return ConversationType.plantCare;
      case 'botanical_advice':
        return ConversationType.botanicalAdvice;
      case 'plantcare':
        return ConversationType.plantCare;
      case 'botanicaladvice':
        return ConversationType.botanicalAdvice;
      default:
        return ConversationType.plantCare;
    }
  }
}

class ConversationParticipant {
  final int userId;
  final DateTime? lastReadAt;
  final String? lastName;
  final String? firstName;
  final String? email;

  ConversationParticipant({
    required this.userId,
    this.lastReadAt,
    this.lastName,
    this.firstName,
    this.email,
  });

  factory ConversationParticipant.fromJson(Map<String, dynamic> json) {
    final userId = json['user_id'] ?? json['id'] ?? 0;
    final lastName = json['last_name'] ?? '';
    final firstName = json['first_name'] ?? '';
    final email = json['email'] ?? '';
    
    return ConversationParticipant(
      userId: userId is String ? int.parse(userId) : userId,
      lastReadAt: json['last_read_at'] != null
          ? DateTime.parse(json['last_read_at'])
          : null,
      lastName: lastName,
      firstName: firstName,
      email: email,
    );
  }

  Map<String, dynamic> toJson() => {
        'user_id': userId,
        'last_read_at': lastReadAt?.toIso8601String(),
        'last_name': lastName,
        'first_name': firstName,
        'email': email,
      };
}

class PlantInfo {
  final int id;
  final String name;
  final String? species;

  PlantInfo({
    required this.id,
    required this.name,
    this.species,
  });

  factory PlantInfo.fromJson(Map<String, dynamic> json) {
    return PlantInfo(
      id: json['id'],
      name: json['name'],
      species: json['species'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'species': species,
      };
}

class PlantCareInfo {
  final int id;
  final DateTime startDate;
  final DateTime endDate;
  final int ownerId;
  final int caretakerid;

  PlantCareInfo({
    required this.id,
    required this.startDate,
    required this.endDate,
    required this.ownerId,
    required this.caretakerid,
  });

  factory PlantCareInfo.fromJson(Map<String, dynamic> json) {
    return PlantCareInfo(
      id: json['id'],
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      ownerId: json['owner_id'],
      caretakerid: json['caretaker_id'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'start_date': startDate.toIso8601String(),
        'end_date': endDate.toIso8601String(),
        'owner_id': ownerId,
        'caretaker_id': caretakerid,
      };
}

class Conversation {
  final int id;
  final ConversationType type;
  final int? relatedId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<ConversationParticipant> participants;
  final Message? lastMessage;
  final int unreadCount;
  final PlantInfo? plantInfo;
  final PlantCareInfo? plantCareInfo;

  Conversation({
    required this.id,
    required this.type,
    this.relatedId,
    required this.createdAt,
    required this.updatedAt,
    required this.participants,
    this.lastMessage,
    required this.unreadCount,
    this.plantInfo,
    this.plantCareInfo,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    try {
      // Parse participants de manière sécurisée
      List<ConversationParticipant> participantsList = [];
      if (json['participants'] != null) {
        try {
          participantsList = (json['participants'] as List)
              .map((p) {
                try {
                  return ConversationParticipant.fromJson(p);
                } catch (e) {
                  return null;
                }
              })
              .where((p) => p != null)
              .cast<ConversationParticipant>()
              .toList();
        } catch (e) {
          // Silencieux
        }
      }
      
      // Parse lastMessage de manière sécurisée
      Message? lastMsg;
      if (json['last_message'] != null) {
        try {
          lastMsg = Message.fromJson(json['last_message']);
        } catch (e) {
          // Silencieux
        }
      }
      
      // Parse plantInfo de manière sécurisée
      PlantInfo? plantInfoObj;
      if (json['plant_info'] != null) {
        try {
          plantInfoObj = PlantInfo.fromJson(json['plant_info']);
        } catch (e) {
          // Silencieux
        }
      }
      
      // Parse plantCareInfo de manière sécurisée
      PlantCareInfo? plantCareInfoObj;
      if (json['plant_care_info'] != null) {
        try {
          plantCareInfoObj = PlantCareInfo.fromJson(json['plant_care_info']);
        } catch (e) {
          // Silencieux
        }
      }
      
      final conversation = Conversation(
        id: json['id'] is String ? int.parse(json['id']) : json['id'],
        type: ConversationType.fromJson(json['type'] ?? 'plant_care'),
        relatedId: json['related_id'],
        createdAt: DateTime.parse(json['created_at']),
        updatedAt: DateTime.parse(json['updated_at']),
        participants: participantsList,
        lastMessage: lastMsg,
        unreadCount: json['unread_count'] ?? 0,
        plantInfo: plantInfoObj,
        plantCareInfo: plantCareInfoObj,
      );
      
      return conversation;
    } catch (e) {
      rethrow;
    }
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type.toJson(),
        'related_id': relatedId,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'participants': participants.map((p) => p.toJson()).toList(),
        'last_message': lastMessage?.toJson(),
        'unread_count': unreadCount,
        'plant_info': plantInfo?.toJson(),
        'plant_care_info': plantCareInfo?.toJson(),
      };

  // Méthodes utilitaires pour l'affichage
  String getTitle(int currentUserId) {
    // Récupérer le nom de l'interlocuteur
    String participantName = 'Inconnu';
    if (participants.isNotEmpty) {
      // Toujours chercher le participant qui n'est PAS l'utilisateur actuel
      ConversationParticipant? otherParticipant = participants.firstWhere(
        (p) => p.userId != currentUserId,
        orElse: () => participants.first, // Fallback si pas trouvé
      );
      
      // Construire le nom complet
      final firstName = otherParticipant.firstName ?? '';
      final lastName = otherParticipant.lastName ?? '';
      final fullName = '$firstName $lastName'.trim();
      
      if (fullName.isNotEmpty) {
        participantName = fullName;
      }
    }
    
    // Construire le titre avec contexte
    if (type == ConversationType.plantCare && plantInfo != null) {
      final plant = plantInfo!;
      return '$participantName - Garde ${plant.name}';
    } else if (type == ConversationType.botanicalAdvice) {
      return '$participantName - Conseil botanique';
    }
    
    // Fallback
    return participantName;
  }

  String getSubtitle(int currentUserId) {
    if (type == ConversationType.plantCare && plantCareInfo != null) {
      final careInfo = plantCareInfo!;
      final startDate = careInfo.startDate;
      final endDate = careInfo.endDate;
      return 'Du ${startDate.day}/${startDate.month}/${startDate.year} au ${endDate.day}/${endDate.month}/${endDate.year}';
    }
    return '';
  }

  String getEmptyMessage(int currentUserId) {
    if (participants.isNotEmpty) {
      final otherParticipant = participants.first;
      final participantName = '${otherParticipant.firstName ?? ''} ${otherParticipant.lastName ?? ''}'.trim();
      return 'Conversation vide. Envoyez votre premier message à $participantName pour conseils ou autre.';
    }
    return 'Conversation vide. Envoyez votre premier message.';
  }

  bool get isEmpty => lastMessage == null;
} 
