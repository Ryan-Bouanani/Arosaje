# Architecture de l'application A'rosa-je

## Vue d'ensemble de l'architecture

```mermaid
graph TB
    subgraph "Clients"
        Mobile[Mobile Flutter<br/>Port 5000]
        Web[Web Nuxt.js<br/>Port 3000]
    end
    
    subgraph "Gateway & API"
        API[FastAPI Backend<br/>Port 8000]
        WS[WebSocket Server<br/>Port 8000]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Port 5432)]
        Redis[(Redis Cache<br/>Port 6379)]
    end
    
    subgraph "Monitoring Stack"
        Grafana[Grafana<br/>Port 3001]
        Prometheus[Prometheus<br/>Port 9090]
        InfluxDB[(InfluxDB<br/>Port 8086)]
    end
    
    Mobile -->|HTTP/HTTPS| API
    Mobile -->|WebSocket| WS
    Web -->|HTTP/HTTPS| API
    Web -->|WebSocket| WS
    
    API -->|SQLAlchemy ORM| PG
    API -->|Cache & Rate Limit| Redis
    WS -->|Session Store| Redis
    
    API -->|Metrics| Prometheus
    API -->|Time Series| InfluxDB
    Prometheus --> Grafana
    InfluxDB --> Grafana
```

## Architecture en couches

```mermaid
graph LR
    subgraph "Presentation Layer"
        UI1[Flutter Mobile UI]
        UI2[Vue.js Web UI]
    end
    
    subgraph "Application Layer"
        AUTH[Authentication<br/>JWT]
        BL[Business Logic]
        VAL[Validation<br/>Pydantic]
        MSG[Messaging<br/>WebSocket]
    end
    
    subgraph "Domain Layer"
        Models[Domain Models]
        Services[Services]
        Repos[Repositories]
    end
    
    subgraph "Infrastructure Layer"
        ORM[SQLAlchemy]
        Cache[Redis Client]
        Email[SMTP Service]
        Storage[File Storage]
    end
    
    UI1 --> AUTH
    UI2 --> AUTH
    AUTH --> BL
    BL --> VAL
    BL --> MSG
    BL --> Services
    Services --> Repos
    Repos --> ORM
    Services --> Cache
    Services --> Email
    Services --> Storage
```

## Flux de données

### 1. Authentification et autorisation

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant PostgreSQL
    
    Client->>API: POST /auth/login
    API->>PostgreSQL: Verify credentials
    PostgreSQL-->>API: User data
    API->>Redis: Store session
    API-->>Client: JWT Token
    
    Client->>API: Request with JWT
    API->>Redis: Check rate limit
    API->>API: Validate JWT
    API->>PostgreSQL: Fetch data
    PostgreSQL-->>API: Data
    API-->>Client: Response
```

### 2. Messagerie temps réel

```mermaid
sequenceDiagram
    participant Client1
    participant WebSocket
    participant Redis
    participant Client2
    
    Client1->>WebSocket: Connect
    WebSocket->>Redis: Register connection
    
    Client1->>WebSocket: Send message
    WebSocket->>Redis: Publish to channel
    Redis->>WebSocket: Broadcast
    WebSocket->>Client2: Deliver message
    
    Client2->>WebSocket: Typing status
    WebSocket->>Redis: Update status
    Redis->>WebSocket: Broadcast status
    WebSocket->>Client1: Show typing
```

## Composants détaillés

### Backend API (FastAPI)

| Composant | Responsabilité | Technologies |
|-----------|---------------|--------------|
| **Routers** | Endpoints REST | FastAPI routers |
| **Services** | Logique métier | Python classes |
| **Models** | Entités domaine | SQLAlchemy ORM |
| **Schemas** | Validation | Pydantic |
| **Middleware** | Cross-cutting | CORS, Auth, Logging |
| **WebSocket** | Temps réel | WebSocket protocol |

### Base de données PostgreSQL

| Schema | Tables | Index | Contraintes |
|--------|--------|-------|-------------|
| **public** | users, plants, plant_cares | B-tree sur FK | UNIQUE, CHECK |
| **messaging** | conversations, messages | GIN pour recherche | CASCADE DELETE |
| **monitoring** | audit_logs, metrics | BRIN temporel | Partitioning |

### Cache Redis

| Usage | Structure | TTL | Pattern |
|-------|-----------|-----|---------|
| **Sessions** | Hash | 24h | session:{user_id} |
| **Rate Limiting** | String | 1min | rate:{ip}:{endpoint} |
| **WebSocket** | PubSub | - | channel:{conv_id} |
| **Cache** | String | 5min | cache:{key} |

## Sécurité

### Couches de sécurité

```mermaid
graph TD
    subgraph "Network Security"
        HTTPS[HTTPS/TLS]
        CORS[CORS Policy]
    end
    
    subgraph "Application Security"
        JWT[JWT Authentication]
        RBAC[Role-Based Access]
        RATE[Rate Limiting]
        VAL2[Input Validation]
    end
    
    subgraph "Data Security"
        HASH[Password Hashing<br/>bcrypt]
        ENC[Data Encryption]
        ANON[Anonymization<br/>SHA-256]
    end
    
    HTTPS --> JWT
    CORS --> JWT
    JWT --> RBAC
    RBAC --> RATE
    RATE --> VAL2
    VAL2 --> HASH
    HASH --> ENC
    ENC --> ANON
```

### Matrice des permissions

| Rôle | Plants | Gardes | Conseils | Admin | Messages |
|------|--------|--------|----------|-------|----------|
| **USER** | CRUD propres | CRUD | Lecture | ❌ | ✅ |
| **BOTANIST** | Lecture | Lecture | CRUD | ❌ | ✅ |
| **ADMIN** | CRUD tous | CRUD tous | Modération | ✅ | ✅ |

## Déploiement

### Architecture Docker

```yaml
Services:
  api:
    - Image: Python 3.11-slim
    - Volumes: ./api:/app, uploads
    - Ports: 8000
    - Depends: postgres, redis
    
  web:
    - Image: Node 18-alpine
    - Volumes: ./web:/app
    - Ports: 3000
    - Depends: api
    
  mobile:
    - Image: Flutter latest
    - Volumes: ./mobile:/app
    - Ports: 5000
    - Depends: api
    
  postgres:
    - Image: PostgreSQL 15
    - Volumes: pgdata
    - Ports: 5432
    
  redis:
    - Image: Redis 7-alpine
    - Volumes: redis-data
    - Ports: 6379
```

### Réseau Docker

```mermaid
graph LR
    subgraph "Docker Network: arosaje-network"
        API[api:8000]
        WEB[web:3000]
        MOBILE[mobile:5000]
        PG[postgres:5432]
        REDIS[redis:6379]
        
        API -.-> PG
        API -.-> REDIS
        WEB -.-> API
        MOBILE -.-> API
    end
    
    subgraph "Host"
        HOST[localhost]
    end
    
    HOST -->|:8000| API
    HOST -->|:3000| WEB
    HOST -->|:5000| MOBILE
```

## Monitoring et observabilité

### Stack de monitoring

```mermaid
graph TD
    subgraph "Metrics Collection"
        APP[Application<br/>Prometheus Client]
        NODE[Node Exporter]
        PG_EXP[Postgres Exporter]
    end
    
    subgraph "Storage"
        PROM[(Prometheus<br/>TSDB)]
        INFLUX[(InfluxDB<br/>Time Series)]
    end
    
    subgraph "Visualization"
        GRAF[Grafana<br/>Dashboards]
        ALERT[Alerting]
    end
    
    APP --> PROM
    NODE --> PROM
    PG_EXP --> PROM
    APP --> INFLUX
    
    PROM --> GRAF
    INFLUX --> GRAF
    GRAF --> ALERT
```

### Métriques clés

| Métrique | Source | Seuil d'alerte | Dashboard |
|----------|--------|----------------|-----------|
| **API Latency** | FastAPI | > 500ms | Performance |
| **Error Rate** | Logs | > 1% | Health |
| **DB Connections** | PostgreSQL | > 80% pool | Database |
| **Cache Hit Rate** | Redis | < 70% | Cache |
| **WebSocket Connections** | API | > 1000 | Real-time |
| **Memory Usage** | Container | > 80% | Resources |

## Scalabilité

### Stratégies de mise à l'échelle

1. **Horizontal Scaling**
   - API: Multiple instances behind load balancer
   - WebSocket: Sticky sessions avec Redis PubSub
   - Database: Read replicas pour lectures

2. **Vertical Scaling**
   - PostgreSQL: Augmentation RAM pour cache
   - Redis: Plus de mémoire pour sessions

3. **Optimisations**
   - CDN pour assets statiques
   - Lazy loading des images
   - Pagination des listes
   - Indexation base de données
   - Query optimization

## Conformité RGPD

### Mesures techniques

- **Minimisation**: Collecte uniquement des données nécessaires
- **Pseudonymisation**: Hash SHA-256 pour exports
- **Chiffrement**: TLS pour transport, bcrypt pour passwords
- **Droit à l'oubli**: CASCADE DELETE sur suppression user
- **Portabilité**: Export JSON des données utilisateur
- **Audit**: Logs de tous les accès aux données sensibles
- **Rétention**: 30 jours pour messages, 1 an pour logs

## Points d'extension

### APIs externes intégrables

- **Météo**: Pour conseils d'arrosage automatiques
- **Reconnaissance d'images**: Identification automatique des espèces
- **Notifications Push**: Firebase Cloud Messaging
- **Paiement**: Pour fonctionnalités premium
- **Maps**: Géolocalisation des gardiens disponibles

### Modules futurs

- Marketplace de plantes
- Forum communautaire
- Système de gamification
- Application IoT pour capteurs
- Intelligence artificielle pour diagnostic