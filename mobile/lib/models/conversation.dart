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

  ConversationParticipant({
    required this.userId,
    this.lastReadAt,
  });

  factory ConversationParticipant.fromJson(Map<String, dynamic> json) {
    return ConversationParticipant(
      userId: json['user_id'],
      lastReadAt: json['last_read_at'] != null
          ? DateTime.parse(json['last_read_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'user_id': userId,
        'last_read_at': lastReadAt?.toIso8601String(),
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

  Conversation({
    required this.id,
    required this.type,
    this.relatedId,
    required this.createdAt,
    required this.updatedAt,
    required this.participants,
    this.lastMessage,
    required this.unreadCount,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] is String ? int.parse(json['id']) : json['id'],
      type: ConversationType.fromJson(json['type'] ?? 'plant_care'),
      relatedId: json['related_id'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      participants: json['participants'] != null
          ? (json['participants'] as List)
              .map((p) => ConversationParticipant.fromJson(p))
              .toList()
          : [],
      lastMessage: json['last_message'] != null
          ? Message.fromJson(json['last_message'])
          : null,
      unreadCount: json['unread_count'] ?? 0,
    );
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
      };
} 