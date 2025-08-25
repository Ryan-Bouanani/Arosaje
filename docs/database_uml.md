# Diagramme UML - Base de données A'rosa-je

## Vue d'ensemble

```mermaid
erDiagram
    USER {
        int id PK
        string email UK
        string password
        string nom
        string prenom
        string telephone
        string localisation
        enum role "USER|BOTANIST|ADMIN"
        boolean is_verified
    }
    
    PLANT {
        int id PK
        string nom
        string espece
        string description
        string photo
        int owner_id FK
    }
    
    PLANT_CARE {
        int id PK
        int plant_id FK
        int owner_id FK
        int caretaker_id FK
        datetime start_date
        datetime end_date
        enum status "PENDING|ACCEPTED|REFUSED|COMPLETED|CANCELLED"
        string care_instructions
    }
    
    PHOTO {
        int id PK
        int plant_id FK
        int plant_care_id FK
        string url
        datetime uploaded_at
        string description
        enum photo_type "BEFORE_CARE|AFTER_CARE|PLANT_STATUS"
    }
    
    ADVICE {
        int id PK
        int plant_id FK
        int botanist_id FK
        string content
        datetime created_at
        enum status "PENDING|VALIDATED|REJECTED"
    }
    
    MESSAGE {
        int id PK
        int conversation_id FK
        int sender_id FK
        string content
        datetime sent_at
        boolean is_read
    }
    
    CONVERSATION {
        int id PK
        enum conversation_type "PLANT_CARE|BOTANICAL_ADVICE|GENERAL"
        datetime created_at
        datetime last_message_at
    }
    
    CONVERSATION_PARTICIPANT {
        int id PK
        int conversation_id FK
        int user_id FK
        datetime joined_at
        datetime last_read_at
    }
    
    USER_TYPING_STATUS {
        int id PK
        int user_id FK
        int conversation_id FK
        boolean is_typing
        datetime last_updated
    }
    
    USER_PRESENCE {
        int id PK
        int user_id FK
        boolean is_online
        datetime last_seen
    }

    %% Relations
    USER ||--o{ PLANT : "possède"
    USER ||--o{ PLANT_CARE : "propriétaire"
    USER ||--o{ PLANT_CARE : "gardien"
    USER ||--o{ ADVICE : "crée (botaniste)"
    USER ||--o{ MESSAGE : "envoie"
    USER ||--o{ CONVERSATION_PARTICIPANT : "participe"
    USER ||--o| USER_PRESENCE : "a"
    USER ||--o{ USER_TYPING_STATUS : "a"
    
    PLANT ||--o{ PLANT_CARE : "concerné par"
    PLANT ||--o{ ADVICE : "reçoit"
    PLANT ||--o{ PHOTO : "a"
    
    PLANT_CARE ||--o{ PHOTO : "documente"
    
    CONVERSATION ||--o{ MESSAGE : "contient"
    CONVERSATION ||--o{ CONVERSATION_PARTICIPANT : "a"
    CONVERSATION ||--o{ USER_TYPING_STATUS : "a"
    
    CONVERSATION_PARTICIPANT }o--|| CONVERSATION : "dans"
    CONVERSATION_PARTICIPANT }o--|| USER : "est"
```

## Description des entités

### USER (Utilisateur)
- **Rôles** : USER (propriétaire/gardien), BOTANIST (conseils), ADMIN (gestion)
- **Vérification** : Les comptes doivent être validés par un admin
- **Relations** : Peut posséder des plantes, garder des plantes, donner des conseils (si botaniste)

### PLANT (Plante)
- **Propriétaire** : Chaque plante appartient à un utilisateur
- **Photos** : Stockage du chemin vers l'image principale
- **Métadonnées** : Nom, espèce, description pour identification

### PLANT_CARE (Garde de plante)
- **Relation tripartite** : Lie propriétaire, gardien et plante
- **Workflow** : États de PENDING à COMPLETED
- **Instructions** : Conseils spécifiques pour la garde

### PHOTO
- **Documentation** : Photos avant/après garde
- **Traçabilité** : Horodatage et type de photo
- **Association** : Liée à une plante ET/OU une garde

### ADVICE (Conseil)
- **Expertise** : Créé uniquement par des botanistes
- **Validation** : Système de modération
- **Contexte** : Lié à une plante spécifique

### MESSAGE & CONVERSATION
- **Messagerie temps réel** : WebSocket pour chat instantané
- **Types de conversation** : Garde, conseil botanique, général
- **Participants multiples** : Support des groupes
- **Statuts** : Typing, présence, lecture

## Optimisations PostgreSQL

### Index
```sql
CREATE INDEX idx_plant_owner ON plants(owner_id);
CREATE INDEX idx_plant_care_status ON plant_cares(status);
CREATE INDEX idx_message_conversation ON messages(conversation_id, sent_at DESC);
CREATE INDEX idx_advice_plant ON advices(plant_id);
CREATE INDEX idx_user_email ON users(email);
```

### Contraintes
```sql
ALTER TABLE plant_cares ADD CONSTRAINT check_dates 
  CHECK (end_date IS NULL OR end_date > start_date);

ALTER TABLE users ADD CONSTRAINT check_role 
  CHECK (role IN ('USER', 'BOTANIST', 'ADMIN'));
```

### Fonctionnalités PostgreSQL utilisées
- **JSONB** : Pour stocker des métadonnées flexibles
- **Full-text search** : Recherche dans les descriptions
- **Triggers** : Mise à jour automatique des timestamps
- **Partitioning** : Pour les tables de messages (si volume important)

## Conformité RGPD

- **Anonymisation** : Fonctions de hachage SHA-256 pour les exports
- **Droit à l'oubli** : CASCADE DELETE sur les relations utilisateur
- **Rétention** : Politique de 30 jours pour les messages
- **Audit** : Tables de logs séparées (non montrées ici)