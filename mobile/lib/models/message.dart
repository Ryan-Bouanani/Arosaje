class Message {
  final int id;
  final String content;
  final int? senderId;
  final int conversationId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool isRead;

  Message({
    required this.id,
    required this.content,
    this.senderId,
    required this.conversationId,
    required this.createdAt,
    required this.updatedAt,
    required this.isRead,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] is String ? int.parse(json['id']) : json['id'],
      content: json['content'] ?? '',
      senderId: json['sender_id'] != null 
          ? (json['sender_id'] is String ? int.parse(json['sender_id']) : json['sender_id'])
          : null,
      conversationId: json['conversation_id'] is String 
          ? int.parse(json['conversation_id']) 
          : json['conversation_id'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      isRead: json['is_read'] ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'content': content,
        'sender_id': senderId,
        'conversation_id': conversationId,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'is_read': isRead,
      };
} 