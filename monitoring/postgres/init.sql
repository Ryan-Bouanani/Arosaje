-- Base de données de monitoring séparée pour respecter les exigences
-- Création des tables pour les logs structurés et métriques business

-- Extension pour les UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table pour les logs d'API avec données anonymisées
CREATE TABLE api_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    message TEXT,
    user_hash VARCHAR(64), -- Hash anonymisé de l'utilisateur (RGPD compliant)
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms INTEGER,
    user_agent_hash VARCHAR(64), -- Hash du user agent pour anonymisation
    ip_country VARCHAR(2), -- Uniquement le pays pour respecter RGPD
    session_hash VARCHAR(64), -- Hash de session anonymisé
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table pour les métriques d'usage business (anonymisées)
CREATE TABLE business_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    user_hash VARCHAR(64), -- Hash anonymisé
    session_hash VARCHAR(64), -- Hash de session
    platform VARCHAR(20), -- web, mobile, api
    feature_used VARCHAR(100),
    country_code VARCHAR(2), -- Géolocalisation au niveau pays seulement
    app_version VARCHAR(20),
    device_type VARCHAR(50), -- iOS, Android, Desktop
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table pour les événements d'usage (conformité RGPD)
CREATE TABLE usage_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL, -- login, logout, feature_usage, etc.
    user_hash VARCHAR(64), -- Hash anonymisé
    session_hash VARCHAR(64),
    platform VARCHAR(20),
    page_path VARCHAR(255),
    action VARCHAR(100),
    duration_seconds INTEGER,
    properties JSONB, -- Propriétés additionnelles anonymisées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table pour les erreurs et crashes (anonymisées)
CREATE TABLE error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    error_type VARCHAR(50) NOT NULL,
    error_message TEXT,
    stack_trace TEXT,
    user_hash VARCHAR(64), -- Hash anonymisé
    session_hash VARCHAR(64),
    platform VARCHAR(20),
    app_version VARCHAR(20),
    device_info VARCHAR(100), -- Informations anonymisées du device
    url_path VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table pour les métriques de performance
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metric_type VARCHAR(50) NOT NULL, -- page_load_time, api_response_time, etc.
    value_ms INTEGER,
    endpoint VARCHAR(255),
    user_hash VARCHAR(64), -- Hash anonymisé
    session_hash VARCHAR(64),
    platform VARCHAR(20),
    connection_type VARCHAR(20), -- wifi, mobile, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour optimiser les requêtes fréquentes
CREATE INDEX idx_api_logs_timestamp ON api_logs(timestamp);
CREATE INDEX idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX idx_api_logs_status_code ON api_logs(status_code);

CREATE INDEX idx_business_metrics_timestamp ON business_metrics(timestamp);
CREATE INDEX idx_business_metrics_name ON business_metrics(metric_name);
CREATE INDEX idx_business_metrics_platform ON business_metrics(platform);

CREATE INDEX idx_usage_events_timestamp ON usage_events(timestamp);
CREATE INDEX idx_usage_events_type ON usage_events(event_type);
CREATE INDEX idx_usage_events_platform ON usage_events(platform);

CREATE INDEX idx_error_logs_timestamp ON error_logs(timestamp);
CREATE INDEX idx_error_logs_type ON error_logs(error_type);
CREATE INDEX idx_error_logs_platform ON error_logs(platform);

CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_performance_metrics_type ON performance_metrics(metric_type);

-- Politique de rétention automatique (conformité RGPD)
-- Les données seront supprimées automatiquement après 30 jours
CREATE OR REPLACE FUNCTION cleanup_old_data() RETURNS void AS $$
BEGIN
    -- Suppression des données de plus de 30 jours
    DELETE FROM api_logs WHERE created_at < NOW() - INTERVAL '30 days';
    DELETE FROM business_metrics WHERE created_at < NOW() - INTERVAL '30 days';
    DELETE FROM usage_events WHERE created_at < NOW() - INTERVAL '30 days';
    DELETE FROM error_logs WHERE created_at < NOW() - INTERVAL '30 days';
    DELETE FROM performance_metrics WHERE created_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Créer une fonction pour anonymiser les données (conformité RGPD)
CREATE OR REPLACE FUNCTION anonymize_user_id(user_id TEXT) RETURNS VARCHAR(64) AS $$
BEGIN
    -- Utilise SHA-256 pour anonymiser les IDs utilisateurs
    RETURN encode(digest(user_id || 'arosaje_salt_2024', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Fonction pour anonymiser les sessions
CREATE OR REPLACE FUNCTION anonymize_session(session_id TEXT) RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(session_id || 'session_salt_2024', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Fonction pour anonymiser les user agents
CREATE OR REPLACE FUNCTION anonymize_user_agent(user_agent TEXT) RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(user_agent || 'ua_salt_2024', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Créer un utilisateur pour les applications
CREATE USER app_monitoring WITH PASSWORD 'app_monitoring_2024';

-- Droits pour l'application
GRANT INSERT, SELECT ON ALL TABLES IN SCHEMA public TO app_monitoring;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_monitoring;

-- Commentaires sur les tables pour documentation
COMMENT ON TABLE api_logs IS 'Logs des API avec données anonymisées conformes RGPD';
COMMENT ON TABLE business_metrics IS 'Métriques business anonymisées pour analytics';
COMMENT ON TABLE usage_events IS 'Événements d''usage anonymisés';
COMMENT ON TABLE error_logs IS 'Logs d''erreurs et crashes anonymisés';
COMMENT ON TABLE performance_metrics IS 'Métriques de performance anonymisées'; 