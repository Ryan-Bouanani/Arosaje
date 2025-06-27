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
  final String? nom;
  final String? prenom;
  final String? email;

  ConversationParticipant({
    required this.userId,
    this.lastReadAt,
    this.nom,
    this.prenom,
    this.email,
  });

  factory ConversationParticipant.fromJson(Map<String, dynamic> json) {
    print('Parsing participant: $json');
    return ConversationParticipant(
      userId: json['user_id'] ?? json['id'],
      lastReadAt: json['last_read_at'] != null
          ? DateTime.parse(json['last_read_at'])
          : null,
      nom: json['nom'],
      prenom: json['prenom'],
      email: json['email'],
    );
  }

  Map<String, dynamic> toJson() => {
        'user_id': userId,
        'last_read_at': lastReadAt?.toIso8601String(),
        'nom': nom,
        'prenom': prenom,
        'email': email,
      };
}

class PlantInfo {
  final int id;
  final String nom;
  final String? espece;

  PlantInfo({
    required this.id,
    required this.nom,
    this.espece,
  });

  factory PlantInfo.fromJson(Map<String, dynamic> json) {
    return PlantInfo(
      id: json['id'],
      nom: json['nom'],
      espece: json['espece'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'nom': nom,
        'espece': espece,
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
      print('Parsing conversation with JSON: $json');
      
      // Parse participants de manière sécurisée
      List<ConversationParticipant> participantsList = [];
      if (json['participants'] != null) {
        try {
          participantsList = (json['participants'] as List)
              .map((p) {
                try {
                  return ConversationParticipant.fromJson(p);
                } catch (e) {
                  print('Error parsing participant $p: $e');
                  return null;
                }
              })
              .where((p) => p != null)
              .cast<ConversationParticipant>()
              .toList();
        } catch (e) {
          print('Error parsing participants list: $e');
        }
      }
      
      // Parse lastMessage de manière sécurisée
      Message? lastMsg;
      if (json['last_message'] != null) {
        try {
          lastMsg = Message.fromJson(json['last_message']);
        } catch (e) {
          print('Error parsing last message: $e');
        }
      }
      
      // Parse plantInfo de manière sécurisée
      PlantInfo? plantInfoObj;
      if (json['plant_info'] != null) {
        try {
          plantInfoObj = PlantInfo.fromJson(json['plant_info']);
        } catch (e) {
          print('Error parsing plant info: $e');
        }
      }
      
      // Parse plantCareInfo de manière sécurisée
      PlantCareInfo? plantCareInfoObj;
      if (json['plant_care_info'] != null) {
        try {
          plantCareInfoObj = PlantCareInfo.fromJson(json['plant_care_info']);
        } catch (e) {
          print('Error parsing plant care info: $e');
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
      
      print('Successfully parsed conversation ${conversation.id}');
      return conversation;
    } catch (e) {
      print('Error in Conversation.fromJson: $e');
      print('JSON data: $json');
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
    if (type == ConversationType.plantCare && plantInfo != null && plantCareInfo != null) {
      return 'Garde de ${plantInfo!.nom}';
    } else if (type == ConversationType.botanicalAdvice) {
      return 'Conseil botanique';
    }
    return 'Conversation';
  }

  String getSubtitle(int currentUserId) {
    if (type == ConversationType.plantCare && plantCareInfo != null) {
      final startDate = plantCareInfo!.startDate;
      final endDate = plantCareInfo!.endDate;
      return 'Du ${startDate.day}/${startDate.month}/${startDate.year} au ${endDate.day}/${endDate.month}/${endDate.year}';
    }
    return '';
  }

  String getEmptyMessage(int currentUserId) {
    if (participants.isNotEmpty) {
      final otherParticipant = participants.first;
      final participantName = '${otherParticipant.prenom ?? ''} ${otherParticipant.nom ?? ''}'.trim();
      return 'Conversation vide. Envoyez votre premier message à $participantName pour conseils ou autre.';
    }
    return 'Conversation vide. Envoyez votre premier message.';
  }

  bool get isEmpty => lastMessage == null;
} 