# Infrastructure de Monitoring Arosa-je

## 📋 Vue d'ensemble

Cette documentation décrit l'infrastructure de monitoring mise en place pour l'application Arosa-je, **conforme à la réglementation européenne (RGPD)**.

## 🎯 Objectifs

- **Collecter des données d'usage anonymisées** pour améliorer l'application
- **Surveiller les performances** techniques de l'infrastructure
- **Analyser les tendances d'utilisation** sans compromettre la vie privée
- **Respecter intégralement le RGPD** et la réglementation européenne

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                      │
├─────────────────┬─────────────────┬─────────────────────┤
│   API FastAPI   │   Web Next.js   │   Mobile Flutter    │
│   (Port 8000)   │   (Port 3000)   │   (Port 5000)       │
└─────────┬───────┴─────────┬───────┴─────────┬───────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────┐
│              Monitoring Infrastructure                  │
├─────────────────┬─────────────────┬─────────────────────┤
│   Prometheus    │     Loki        │     InfluxDB        │
│ (Métriques      │   (Logs)        │  (Métriques         │
│  techniques)    │ (Port 3100)     │   Business)         │
│ (Port 9090)     │                 │ (Port 8086)         │
├─────────────────┼─────────────────┼─────────────────────┤
│              Grafana Dashboards                        │
│            (Port 3001)                                  │
├─────────────────┴─────────────────┴─────────────────────┤
│         PostgreSQL Monitoring Database                 │
│         (Données anonymisées - Port 5434)              │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Démarrage Rapide

### 1. Prérequis

- Docker 20.0+
- Docker Compose 2.0+
- 6GB RAM minimum
- 50GB d'espace disque libre

### 2. Installation

```bash
# Cloner le repository (si pas déjà fait)
git clone <repo-url>
cd EPSI-MSPR6.1

# Démarrer l'infrastructure de monitoring
./start-monitoring.sh

# Attendre que tous les services soient prêts (~2-3 minutes)
```

### 3. Vérification

Vérifiez que tous les services sont accessibles :

- **Grafana** : http://localhost:3001 (admin/arosaje_grafana_2024)
- **Prometheus** : http://localhost:9090
- **InfluxDB** : http://localhost:8086

## 📊 Services de Monitoring

### Grafana (Port 3001)
- **Interface de visualisation unifiée**
- **Dashboards pré-configurés**
- **Alertes et notifications**

**Identifiants par défaut :**
- Utilisateur : `admin`
- Mot de passe : `arosaje_grafana_2024`

### Prometheus (Port 9090)
- **Collecte des métriques techniques**
- **Surveillance en temps réel**
- **Stockage time-series optimisé**

### Loki (Port 3100)
- **Collecte et indexation des logs**
- **Recherche et filtrage avancés**
- **Corrélation avec les métriques**

### InfluxDB (Port 8086)
- **Base de données time-series pour métriques business**
- **Optimisée pour les données temporelles**
- **Requêtes analytiques avancées**

### PostgreSQL Monitoring (Port 5434)
- **Stockage des données anonymisées**
- **Logs structurés conformes RGPD**
- **Rétention automatique (30 jours)**

## 📈 Dashboards Disponibles

### 1. System Overview
**Localisation :** `monitoring/grafana/dashboards/system/system-overview.json`

**Métriques surveillées :**
- Utilisation CPU/RAM/Disque
- Statut des containers
- Trafic réseau
- Performance des services

### 2. API Performance
**Localisation :** `monitoring/grafana/dashboards/application/api-performance.json`

**Métriques surveillées :**
- Requêtes par seconde
- Temps de réponse
- Taux d'erreur
- Distribution des codes de statut

### 3. User Analytics (RGPD Compliant)
**Localisation :** `monitoring/grafana/dashboards/business/user-analytics.json`

**Métriques anonymisées :**
- Utilisateurs actifs (hachés)
- Utilisation des fonctionnalités
- Distribution géographique (pays uniquement)
- Tendances d'usage

## 🔒 Conformité RGPD

### Données Collectées (Anonymisées)

#### ✅ Métriques Techniques (Non-personnelles)
- Nombre de requêtes par endpoint
- Temps de réponse des API
- Utilisation CPU/RAM/Disque
- Erreurs 4xx/5xx
- Statut des services

#### ✅ Métriques Business (Anonymisées)
- Hash SHA-256 des IDs utilisateurs
- Hash SHA-256 des sessions
- Fonctionnalités utilisées
- Géolocalisation niveau pays uniquement
- Version d'application et type d'appareil

#### ❌ Données NON Collectées
- Adresses IP complètes
- Informations personnelles identifiables
- Contenu des messages privés
- Données de géolocalisation précises
- Historique de navigation détaillé

### Fonctions d'Anonymisation

```sql
-- Anonymisation des IDs utilisateurs
CREATE OR REPLACE FUNCTION anonymize_user_id(user_id TEXT) RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(user_id || 'arosaje_salt_2024', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Anonymisation des sessions
CREATE OR REPLACE FUNCTION anonymize_session(session_id TEXT) RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(session_id || 'session_salt_2024', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;
```

### Politique de Rétention

- **Durée de conservation :** 30 jours maximum
- **Suppression automatique :** Fonction `cleanup_old_data()` 
- **Droit à l'oubli :** Respecté par l'anonymisation
- **Portabilité :** Données exportables au format JSON

## ⚙️ Configuration

### Variables d'Environnement

Créer un fichier `.env.monitoring` :

```bash
# Base de données monitoring
MONITORING_DB_HOST=monitoring-postgres
MONITORING_DB_PORT=5432
MONITORING_DB_NAME=monitoring_db
MONITORING_DB_USER=app_monitoring
MONITORING_DB_PASSWORD=app_monitoring_2024

# InfluxDB
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=arosaje-token-12345678
INFLUXDB_ORG=arosaje
INFLUXDB_BUCKET=metrics

# Anonymisation
MONITORING_SALT=arosaje_salt_2024
```

### Ports Utilisés

| Service | Port | Description |
|---------|------|-------------|
| Grafana | 3001 | Interface de visualisation |
| Prometheus | 9090 | Métriques techniques |
| Loki | 3100 | Collecte de logs |
| InfluxDB | 8086 | Métriques business |
| PostgreSQL | 5434 | Base de données monitoring |
| Node Exporter | 9100 | Métriques système |
| cAdvisor | 8080 | Métriques containers |

## 📝 Utilisation

### Démarrer le Monitoring

```bash
# Démarrer tous les services de monitoring
./start-monitoring.sh

# Ou manuellement
docker-compose -f docker-compose.monitoring.yml up -d
```

### Démarrer l'Application avec Monitoring

```bash
# Démarrer l'application normale
docker-compose up -d

# L'API exposera automatiquement les métriques sur /metrics
```

### Arrêter le Monitoring

```bash
# Arrêter uniquement le monitoring
docker-compose -f docker-compose.monitoring.yml down

# Arrêter tout (application + monitoring)
docker-compose down
docker-compose -f docker-compose.monitoring.yml down
```

## 🔧 Maintenance

### Nettoyage des Données

```sql
-- Nettoyer manuellement les données de plus de 30 jours
SELECT cleanup_old_data();

-- Vérifier l'espace utilisé
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public';
```

### Backup

```bash
# Backup de la configuration Grafana
docker exec arosa-je-grafana grafana-cli admin export-dashboard

# Backup de la base de données monitoring
docker exec arosa-je-monitoring-postgres pg_dump -U monitoring monitoring_db > backup_monitoring.sql
```

### Mise à jour

```bash
# Mise à jour des images Docker
docker-compose -f docker-compose.monitoring.yml pull
docker-compose -f docker-compose.monitoring.yml up -d
```

## 🚨 Alertes

### Configuration des Alertes Grafana

1. Accéder à Grafana (http://localhost:3001)
2. Aller dans **Alerting** > **Alert Rules**
3. Créer des alertes pour :
   - CPU > 80%
   - Mémoire > 85%
   - Taux d'erreur > 5%
   - Temps de réponse > 2s

### Notifications

Configurer les canaux de notification dans Grafana :
- Email
- Slack
- Webhook

## 📊 Métriques API

L'API expose les métriques Prometheus sur `/metrics` :

```bash
# Voir les métriques de l'API
curl http://localhost:8000/metrics

# Métriques principales disponibles :
# - arosaje_requests_total
# - arosaje_request_duration_seconds
# - arosaje_active_users
# - arosaje_feature_usage_total
# - arosaje_errors_total
```

## 🔍 Dépannage

### Problèmes Courants

#### Services non accessibles
```bash
# Vérifier les logs
docker-compose -f docker-compose.monitoring.yml logs [service-name]

# Vérifier l'état des containers
docker ps | grep arosa-je
```

#### Problèmes de connectivité
```bash
# Vérifier les réseaux Docker
docker network ls
docker network inspect arosa-je-network

# Tester la connectivité
docker exec arosa-je-grafana ping prometheus
```

#### Problèmes de performance
```bash
# Vérifier l'utilisation des ressources
docker stats

# Nettoyer les volumes non utilisés
docker volume prune
```

## 📞 Support

### Logs Important à Consulter

- **Application :** `api/logs/`, `web/logs/`
- **Monitoring :** `docker-compose -f docker-compose.monitoring.yml logs`
- **Grafana :** http://localhost:3001/explore

### Fichiers de Configuration

- **Prometheus :** `monitoring/prometheus/prometheus.yml`
- **Loki :** `monitoring/loki/config.yml`
- **Grafana :** `monitoring/grafana/provisioning/`

## 📚 Ressources Additionnelles

- [Documentation Grafana](https://grafana.com/docs/)
- [Documentation Prometheus](https://prometheus.io/docs/)
- [Documentation InfluxDB](https://docs.influxdata.com/)
- [RGPD - Guide Officiel](https://gdpr.eu/)

---

**⚠️ Important :** Cette infrastructure respecte intégralement le RGPD grâce à l'anonymisation systématique des données et la limitation de la rétention à 30 jours. 