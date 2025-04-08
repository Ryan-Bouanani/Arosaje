# Justification par le Code - MSPR TPTE502

## 1. Développer des composants d'accès aux données SQL et NoSQL

**Justification** : L'application A'rosa-je démontre une maîtrise avancée des composants d'accès aux données grâce à une architecture hybride SQL/NoSQL. SQLAlchemy est utilisé pour la persistance structurée, tandis que Redis apporte performance et réactivité pour les données volatiles. Cette approche optimise les performances tout en maintenant l'intégrité des données, essentielle pour une application de gestion de plantes où les données doivent être à la fois persistantes et rapidement accessibles.

### SQLAlchemy (SQL)
```python
# api/utils/database.py - Configuration SQLAlchemy optimisée
Base = declarative_base()
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# api/models/photo.py - Modèle avec relations et contraintes
class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)  # 'plant', 'garde_start', 'garde_end'
    plant_id = Column(Integer, ForeignKey("plants.id"))
    plant = relationship("Plant", back_populates="photos")
```

### Redis (NoSQL)
```python
# api/crud/photo.py - Utilisation avancée du cache Redis
def get_plant_photos(self, db: Session, plant_id: int) -> Dict[str, List[PhotoResponse]]:
    # Vérifier le cache Redis
    cache_key = f"plant_photos:{plant_id}"
    cached_photos = self.redis_client.get(cache_key)
    
    if cached_photos:
        return {"photos": json.loads(cached_photos)}
        
    # Si pas en cache, récupérer depuis la base de données
    photos = db.query(Photo).filter(Photo.plant_id == plant_id).all()
    
    # Convertir et mettre en cache
    photos_data = [PhotoResponse(...).model_dump(mode='json') for photo in photos]
    self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(photos_data))
    
    return {"photos": photos_data}
```

## 2. Développer des composants dans le langage d'une base de données

**Justification** : L'application exploite pleinement les capacités avancées de SQLAlchemy ORM pour modéliser des relations complexes et des contraintes métier. Les migrations Alembic assurent l'évolution cohérente du schéma. Cette implémentation respecte les principes de normalisation et d'intégrité référentielle tout en facilitant l'évolution de la base de données, un facteur clé pour la maintenabilité à long terme de l'application.

### Modèles et Relations Complexes
```python
# api/models/message.py - Relations multiples avec cascades
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ConversationType))
    related_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations avec comportements de cascade
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    participants = relationship("ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan")
    plant_care = relationship("PlantCare", back_populates="conversation", uselist=False)
    typing_users = relationship("UserTypingStatus", back_populates="conversation", cascade="all, delete-orphan")
```

### Migrations et Gestion du Schéma
```python
# api/alembic/env.py - Configuration avancée des migrations
from alembic import context
from utils.database import Base
from models import user, plant, advice, photo, plant_care

# Import automatique des modèles pour la détection des changements
target_metadata = Base.metadata

def run_migrations_online():
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # Compare les types pour détecter les changements
        )
        with context.begin_transaction():
            context.run_migrations()
```

## 3. Définir l'architecture logicielle d'une application

**Justification** : L'architecture microservices adoptée démontre une vision orientée évolutivité et maintenabilité. Chaque service (API, Web, Mobile, Redis) est conteneurisé et encapsulé, avec une séparation claire des responsabilités et des interfaces bien définies. Les services de santé (healthchecks) et les dépendances explicites assurent la robustesse et la résilience du système, essentielles pour une application qui doit être toujours disponible pour les utilisateurs.

### Architecture Microservices Optimisée
```yaml
# docker-compose.yml - Architecture complète avec dépendances et healthchecks
services:
  api:
    container_name: arosa-je-api
    image: arosa-je-api
    volumes:
      - ./api:/app
      - ./api/assets/database:/app/assets/database
      - ./api/assets/img:/app/assets/img
    depends_on:
      api-redis:
        condition: service_healthy
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:8000/health" ]
      interval: 10s
      retries: 3

  web:
    container_name: arosa-je-web
    depends_on:
      - api
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:3000" ]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  api-redis:
    image: redis:7-alpine
    container_name: arosa-je-api-redis
    healthcheck:
      test: [ "CMD", "redis-cli", "ping" ]
```

### API Structurée avec Séparation des Préoccupations
```python
# api/main.py - Structure modulaire de l'API
app = FastAPI(title=PROJECT_NAME, version=VERSION)

# Middleware de sécurité et performance
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS
)

# Routers avec séparation des préoccupations
app.include_router(auth.router)
app.include_router(plant.router)
app.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])

# Point de santé pour les healthchecks
@app.get("/health", tags=["monitoring"])
async def health_check():
    return {"status": "healthy"}
```

## 4. Développer des composants métiers

**Justification** : La conception des composants métiers suit le principe de responsabilité unique avec un CRUD générique réutilisable et des implémentations spécifiques pour les cas particuliers. L'utilisation de types génériques et de modèles Pydantic assure la cohérence et la validation des données à tous les niveaux. Cette approche réduit la duplication de code et facilite l'évolution des fonctionnalités métier, un avantage crucial pour une application en constante évolution.

### CRUD Générique avec Types Paramétrés
```python
# api/crud/base.py - CRUD générique avec types génériques
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Récupérer un élément par son ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[ModelType]:
        """Récupérer plusieurs éléments avec pagination et filtres dynamiques"""
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
                    
        return query.offset(skip).limit(limit).all()
```

### Logique Métier Spécifique
```python
# api/crud/photo.py - CRUD spécialisé avec logique métier spécifique
class CRUDPhoto(CRUDBase[Photo, PhotoCreate, PhotoCreate]):
    def delete_with_file(self, db: Session, *, id: int) -> bool:
        """Supprime une photo, son fichier et invalide le cache"""
        photo = self.get(db=db, id=id)
        if photo:
            # Invalider le cache
            self.redis_client.delete(f"plant_photos:{photo.plant_id}")
            
            # Supprimer le fichier physique
            ImageHandler.delete_image(photo.filename)
            
            # Supprimer l'entrée en base
            db.delete(photo)
            db.commit()
            return True
        return False
```

## 5. Préparer et exécuter les plans de tests d'une application

**Justification** : L'application intègre une stratégie de test complète avec des tests d'intégration automatisés utilisant Tavern pour valider les workflows complets. Le monitoring des performances permet d'identifier proactivement les problèmes potentiels. Cette approche exhaustive garantit la fiabilité du système et la rapidité de détection des anomalies, deux aspects essentiels pour une application critique manipulant des données sensibles comme les plantes des utilisateurs.

### Tests d'Intégration de Workflow Complet
```yaml
# api/tests/workflows/test_auth_workflow.tavern.yaml - Test complet d'authentification
test_name: Test authentification
marks:
  - usefixtures:
      - api_url
      - test_user_email
      - test_password

stages:
  - name: Test inscription utilisateur
    request:
      url: "{api_url}/auth/register"
      method: POST
      json:
        nom: "Dupont"
        prenom: "Jean"
        email: "{test_user_email}"
        telephone: "0612345678"
        localisation: "Paris"
        password: "{test_password}"
    response:
      status_code: 200
      save:
        json:
          saved_email: email

  - name: Test login
    request:
      url: "{api_url}/auth/login"
      method: POST
      headers:
        content-type: application/x-www-form-urlencoded
      data:
        username: "{saved_email}"
        password: "{test_password}"
    response:
      status_code: 200
      save:
        json:
          auth_token: access_token
```

### Monitoring Avancé des Performances
```python
# api/routers/monitoring.py - Monitoring sécurisé des performances
from fastapi import APIRouter, Depends
from utils.monitoring import get_monitoring_stats
from utils.security import get_current_user

router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(get_current_user)]  # Sécuriser l'accès aux métriques
)

@router.get("/stats")
async def get_stats():
    """Récupère les statistiques de monitoring de l'API"""
    return get_monitoring_stats()
```

## 6. Préparer et exécuter le déploiement d'une application

**Justification** : Le déploiement est entièrement automatisé grâce à Docker et des scripts d'initialisation robustes. Les builds multi-stage optimisent la taille des images et réduisent les vulnérabilités potentielles. Les scripts d'initialisation garantissent une configuration cohérente de l'environnement, un aspect crucial pour éviter les problèmes de déploiement et permettre une mise en production fiable et répétable.

### Docker Multi-stage pour Optimisation des Images
```dockerfile
# api/Dockerfile - Build multi-stage optimisé et sécurisé
FROM python:3.11-alpine as builder

WORKDIR /app

# Installation des dépendances de build
RUN apk add --no-cache gcc musl-dev libffi-dev

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage final avec image minimale
FROM python:3.11-alpine

WORKDIR /app

# Copie uniquement des dépendances nécessaires
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Installation des dépendances minimales
RUN apk add --no-cache sqlite curl

# Optimisation des workers Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--limit-concurrency", "50"]
```

### Scripts d'Initialisation et Déploiement
```bash
# bin/up - Script de déploiement avec gestion des erreurs
cleanup() {
    echo -e "\n\n🛑 Arrêt des conteneurs..."
    
    # Arrêter l'émulateur Android s'il est en cours d'exécution
    stop_android_emulator
    
    if [ "$1" = "all" ]; then
        docker-compose down
        echo "✅ Tous les services ont été arrêtés."
    else
        # Convertir les arguments en array pour gérer plusieurs services
        local services=($@)
        if [ ${#services[@]} -gt 0 ]; then
            # S'assurer que Redis est arrêté si l'API est arrêtée
            if [[ " ${services[@]} " =~ " api " ]]; then
                docker-compose stop api-redis api "${services[@]}"
            else
                docker-compose stop "${services[@]}"
            fi
            # Vérifier si les ports sont toujours utilisés
            for service in "${services[@]}"; do
                # [...code de vérification des ports...]
            done
            echo "✅ Services arrêtés : ${services[*]}"
        fi
    fi
}
```

## 7. Documenter le déploiement d'une application

**Justification** : La documentation est exceptionnellement complète, couvrant tous les aspects de l'installation, de la configuration et du déploiement. Les instructions détaillées, les scripts utilitaires et les solutions de dépannage assurent une expérience fluide pour les développeurs et les opérateurs. Cette approche exemplaire de la documentation garantit que l'application peut être maintenue et déployée par différentes équipes, un atout majeur pour la continuité du projet.

### Documentation Technique Exhaustive
```markdown
# README.md - Documentation détaillée du déploiement
## 📦 Installation et Déploiement

### **Prérequis**
- Docker & Docker Compose
- Git
- Python 3.11+ (pour l'API)

### **Étapes d'installation**
```bash
# Cloner le dépôt
git clone <repository-url>

# Rendre les scripts exécutables
chmod +x bin/up bin/update bin/setup-api bin/setup-env

# Configurer les variables d'environnement
bin/setup-env

# Configurer l'environnement Python pour l'API
bin/setup-api

# Démarrer tous les services
bin/up all
```

### **🛠️ Commandes Utiles**
```bash
# S'attacher à un conteneur spécifique pour le debug
docker attach arosa-je-api    # Pour débugger l'API
docker attach arosa-je-web    # Pour débugger le frontend

# Note: Utilisez CTRL+P CTRL+Q pour se détacher sans arrêter le conteneur
```

### **⚠️ Résolution des Problèmes**
Si `bin/up all` échoue, vérifiez :
1. Que Docker est en cours d'exécution
2. Que les ports requis (8000, 3000, 5000) sont disponibles
```

## 8. Justifier le choix d'un protocole d'authentification

**Justification** : L'implémentation de JWT (JSON Web Tokens) avec une configuration CORS rigoureuse démontre une compréhension approfondie des enjeux de sécurité modernes. Les tokens à durée limitée, la gestion sécurisée des identifiants et la validation stricte des origines CORS permettent d'assurer une authentification robuste et une protection contre les attaques CSRF et XSS, cruciales pour protéger les données sensibles des utilisateurs.

### JWT Sécurisé avec Expiration Contrôlée
```python
# api/utils/security.py - Implémentation JWT complète
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT sécurisé avec expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[dict]:
    """Récupère et valide l'utilisateur à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = user_crud.get(db, id=int(token_data.user_id))
    if user is None:
        raise credentials_exception
    return user
```

### CORS Configuré pour la Sécurité
```python
# api/utils/settings.py - Configuration CORS stricte
# Configuration CORS
CORS_ALLOW_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://web:3000").split(",")
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
CORS_ALLOW_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers"
]
```

## 9. Optimiser configuration d'une mise en container d'une solution

**Justification** : La containerisation est exemplaire avec une optimisation fine des images Docker, des healthchecks complets et une gestion efficace des ressources. Les volumes persistants, les variables d'environnement externalisées et les réseaux dédiés démontrent une maîtrise avancée des meilleures pratiques Docker. Cette configuration assure une haute disponibilité, une isolation de sécurité et des performances optimales, essentielles pour une application critique en production.

### Configuration Docker Optimisée et Résiliente
```yaml
# docker-compose.yml - Configuration Docker complète avec réseaux et volumes
services:
  api:
    container_name: arosa-je-api
    volumes:
      - ./api:/app
      - ./api/assets/database:/app/assets/database
      - ./api/assets/img:/app/assets/img
    environment:
      - PYTHONUNBUFFERED=1
      - GIT_DISCOVERY_ACROSS_FILESYSTEM=1
    networks:
      - arosa-je-network
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:8000/health" ]
      interval: 10s
      timeout: 5s
      retries: 3
  
  api-redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
      - ./redis/users.acl:/data/users.acl:ro
    command: >
      sh -c '
        redis-server --appendonly yes --requirepass "$${REDIS_PASSWORD}" --aclfile /data/users.acl'
    healthcheck:
      test: [ "CMD", "redis-cli", "ping" ]

networks:
  arosa-je-network:
    name: arosa-je-network

volumes:
  redis_data:
```

### Gestion Fine des Ressources et Santé des Conteneurs
```dockerfile
# web/Dockerfile - Optimisation des ressources et healthcheck
ENV NODE_OPTIONS='--no-warnings --max-old-space-size=512'
RUN npm install -g nuxt cross-env

# Nettoyage du cache npm pour réduire la taille de l'image
RUN npm cache clean --force

# Healthcheck pour surveillance proactive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1
``` 