enum AdvicePriority {
  normal('normal', 'Normal', '📋'),
  urgent('urgent', 'Urgent', '🚨'),
  followUp('follow_up', 'Suivi', '📌');

  const AdvicePriority(this.value, this.displayName, this.emoji);
  final String value;
  final String displayName;
  final String emoji;
  
  static AdvicePriority fromString(String value) {
    return values.firstWhere(
      (priority) => priority.value == value,
      orElse: () => AdvicePriority.normal,
    );
  }
}

enum ValidationStatus {
  pending('pending', 'En attente', '⏳'),
  validated('validated', 'Validé', '✅'),
  rejected('rejected', 'Rejeté', '❌'),
  needsRevision('needs_revision', 'À réviser', '⚠️');

  const ValidationStatus(this.value, this.displayName, this.emoji);
  final String value;
  final String displayName;
  final String emoji;
  
  static ValidationStatus fromString(String value) {
    return values.firstWhere(
      (status) => status.value == value,
      orElse: () => ValidationStatus.pending,
    );
  }
}

enum ValidationFilter {
  all('Tous'),
  pending('En attente'),
  validated('Validés'),
  rejected('Rejetés'),
  needsRevision('À réviser');

  const ValidationFilter(this.displayName);
  final String displayName;
}

class BotanistInfo {
  final int id;
  final String prenom;
  final String nom;
  final String email;

  BotanistInfo({
    required this.id,
    required this.prenom,
    required this.nom,
    required this.email,
  });

  String get fullName => '$prenom $nom';

  factory BotanistInfo.fromJson(Map<String, dynamic> json) {
    return BotanistInfo(
      id: json['id'],
      prenom: json['prenom'] ?? '',
      nom: json['nom'] ?? '',
      email: json['email'] ?? '',
    );
  }
}

class Advice {
  final int id;
  final int plantCareId;
  final int botanistId;
  final String title;
  final String content;
  final AdvicePriority priority;
  final ValidationStatus validationStatus;
  final int? validatorId;
  final String? validationComment;
  final DateTime? validatedAt;
  final int version;
  final bool isCurrentVersion;
  final int? previousVersionId;
  final bool ownerNotified;
  final bool botanistNotified;
  final DateTime createdAt;
  final DateTime updatedAt;
  final BotanistInfo? botanist;
  final BotanistInfo? validator;

  Advice({
    required this.id,
    required this.plantCareId,
    required this.botanistId,
    required this.title,
    required this.content,
    required this.priority,
    required this.validationStatus,
    this.validatorId,
    this.validationComment,
    this.validatedAt,
    required this.version,
    required this.isCurrentVersion,
    this.previousVersionId,
    required this.ownerNotified,
    required this.botanistNotified,
    required this.createdAt,
    required this.updatedAt,
    this.botanist,
    this.validator,
  });

  factory Advice.fromJson(Map<String, dynamic> json) {
    return Advice(
      id: json['id'],
      plantCareId: json['plant_care_id'],
      botanistId: json['botanist_id'],
      title: json['title'],
      content: json['content'],
      priority: AdvicePriority.fromString(json['priority']),
      validationStatus: ValidationStatus.fromString(json['validation_status']),
      validatorId: json['validator_id'],
      validationComment: json['validation_comment'],
      validatedAt: json['validated_at'] != null 
          ? DateTime.parse(json['validated_at']) 
          : null,
      version: json['version'],
      isCurrentVersion: json['is_current_version'] ?? true,
      previousVersionId: json['previous_version_id'],
      ownerNotified: json['owner_notified'] ?? false,
      botanistNotified: json['botanist_notified'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      botanist: json['botanist'] != null 
          ? BotanistInfo.fromJson(json['botanist'])
          : null,
      validator: json['validator'] != null 
          ? BotanistInfo.fromJson(json['validator'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'plant_care_id': plantCareId,
      'botanist_id': botanistId,
      'title': title,
      'content': content,
      'priority': priority.value,
      'validation_status': validationStatus.value,
      'validator_id': validatorId,
      'validation_comment': validationComment,
      'validated_at': validatedAt?.toIso8601String(),
      'version': version,
      'is_current_version': isCurrentVersion,
      'previous_version_id': previousVersionId,
      'owner_notified': ownerNotified,
      'botanist_notified': botanistNotified,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'botanist': botanist?.toJson(),
      'validator': validator?.toJson(),
    };
  }
}

extension BotanistInfoToJson on BotanistInfo {
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'prenom': prenom,
      'nom': nom,
      'email': email,
    };
  }
}

class PlantCareWithAdvice {
  final int id;
  final int plantId;
  final DateTime startDate;
  final DateTime endDate;
  final String? careInstructions;
  final String? localisation;
  final AdvicePriority priority;
  final String plantName;
  final String? plantSpecies;
  final String? plantImageUrl;
  final String ownerName;
  final String ownerEmail;
  final Advice? currentAdvice;
  final List<Advice> adviceHistory;
  final bool needsValidation;
  final int validationCount;

  PlantCareWithAdvice({
    required this.id,
    required this.plantId,
    required this.startDate,
    required this.endDate,
    this.careInstructions,
    this.localisation,
    required this.priority,
    required this.plantName,
    this.plantSpecies,
    this.plantImageUrl,
    required this.ownerName,
    required this.ownerEmail,
    this.currentAdvice,
    required this.adviceHistory,
    required this.needsValidation,
    required this.validationCount,
  });

  factory PlantCareWithAdvice.fromJson(Map<String, dynamic> json) {
    return PlantCareWithAdvice(
      id: json['id'],
      plantId: json['plant_id'],
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      careInstructions: json['care_instructions'],
      localisation: json['localisation'],
      priority: AdvicePriority.fromString(json['priority'] ?? 'normal'),
      plantName: json['plant_name'],
      plantSpecies: json['plant_species'],
      plantImageUrl: json['plant_image_url'],
      ownerName: json['owner_name'],
      ownerEmail: json['owner_email'],
      currentAdvice: json['current_advice'] != null 
          ? Advice.fromJson(json['current_advice'])
          : null,
      adviceHistory: (json['advice_history'] as List<dynamic>?)
          ?.map((advice) => Advice.fromJson(advice))
          .toList() ?? [],
      needsValidation: json['needs_validation'] ?? false,
      validationCount: json['validation_count'] ?? 0,
    );
  }
}

class AdviceStats {
  final int totalToReview;
  final int totalReviewed;
  final int urgentCount;
  final int followUpCount;
  final int pendingValidation;
  final int myAdviceCount;
  final int myValidatedCount;
  final int myValidationsDoneCount;

  AdviceStats({
    required this.totalToReview,
    required this.totalReviewed,
    required this.urgentCount,
    required this.followUpCount,
    required this.pendingValidation,
    required this.myAdviceCount,
    this.myValidatedCount = 0,
    this.myValidationsDoneCount = 0,
  });

  factory AdviceStats.fromJson(Map<String, dynamic> json) {
    return AdviceStats(
      totalToReview: json['total_to_review'] ?? 0,
      totalReviewed: json['total_reviewed'] ?? 0,
      urgentCount: json['urgent_count'] ?? 0,
      followUpCount: json['follow_up_count'] ?? 0,
      pendingValidation: json['pending_validation'] ?? 0,
      myAdviceCount: json['my_advice_count'] ?? 0,
      myValidatedCount: json['my_validated_count'] ?? 0,
      myValidationsDoneCount: json['my_validations_done_count'] ?? 0,
    );
  }
}

class AdviceCreate {
  final int plantCareId;
  final String title;
  final String content;
  final AdvicePriority priority;

  AdviceCreate({
    required this.plantCareId,
    required this.title,
    required this.content,
    required this.priority,
  });

  Map<String, dynamic> toJson() {
    return {
      'plant_care_id': plantCareId,
      'title': title,
      'content': content,
      'priority': priority.value,
    };
  }
}


class AdviceValidation {
  final ValidationStatus validationStatus;
  final String? validationComment;

  AdviceValidation({
    required this.validationStatus,
    this.validationComment,
  });

  Map<String, dynamic> toJson() {
    return {
      'validation_status': validationStatus.value,
      'validation_comment': validationComment,
    };
  }
}
