-- TrafficTwin AI Database Schema
-- PostgreSQL

CREATE TABLE traffic_incidents (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_cause VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    corridor VARCHAR(100),
    zone VARCHAR(100),
    junction VARCHAR(100),
    address TEXT,
    priority VARCHAR(20) NOT NULL,
    requires_road_closure BOOLEAN DEFAULT FALSE,
    vehicle_type VARCHAR(50),
    start_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    closed_datetime TIMESTAMP WITH TIME ZONE,
    resolved_datetime TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    actual_clearance_time_minutes INTEGER,
    description TEXT,
    has_embedding BOOLEAN DEFAULT FALSE
);

CREATE TABLE prediction_results (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL,
    predicted_clearance_time FLOAT NOT NULL,
    peak_hour INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (incident_id) REFERENCES traffic_incidents(id)
);

CREATE TABLE severity_scores (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL,
    severity_score FLOAT NOT NULL,
    severity_level VARCHAR(20) NOT NULL,
    priority_weight FLOAT,
    road_closure_weight FLOAT,
    corridor_weight FLOAT,
    vehicle_weight FLOAT,
    peak_hour_weight FLOAT,
    junction_weight FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (incident_id) REFERENCES traffic_incidents(id)
);

CREATE TABLE similar_incidents (
    id SERIAL PRIMARY KEY,
    query_incident_id INTEGER NOT NULL,
    similar_incident_id INTEGER NOT NULL,
    similarity_score FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (query_incident_id) REFERENCES traffic_incidents(id),
    FOREIGN KEY (similar_incident_id) REFERENCES traffic_incidents(id)
);

CREATE TABLE incident_recommendations (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL,
    severity VARCHAR(20) NOT NULL,
    predicted_clearance FLOAT NOT NULL,
    diversion_required BOOLEAN DEFAULT FALSE,
    urgency_level VARCHAR(20) NOT NULL,
    similar_cases_found INTEGER DEFAULT 0,
    estimated_resolution_time FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (incident_id) REFERENCES traffic_incidents(id)
);

-- Indexes for traffic_incidents
CREATE INDEX ix_incident_coordinates
ON traffic_incidents(latitude, longitude);

CREATE INDEX ix_incident_time_range
ON traffic_incidents(start_datetime, closed_datetime);

CREATE INDEX ix_event_type
ON traffic_incidents(event_type);

CREATE INDEX ix_event_cause
ON traffic_incidents(event_cause);

CREATE INDEX ix_corridor
ON traffic_incidents(corridor);

CREATE INDEX ix_priority
ON traffic_incidents(priority);

CREATE INDEX ix_status
ON traffic_incidents(status);

-- Indexes for prediction_results
CREATE INDEX ix_prediction_incident_id
ON prediction_results(incident_id);

-- Indexes for severity_scores
CREATE INDEX ix_severity_incident_id
ON severity_scores(incident_id);

CREATE INDEX ix_severity_level
ON severity_scores(severity_level);

-- Indexes for similar_incidents
CREATE INDEX ix_query_id
ON similar_incidents(query_incident_id);

CREATE INDEX ix_similar_id
ON similar_incidents(similar_incident_id);

-- Indexes for incident_recommendations
CREATE INDEX ix_recommendation_incident_id
ON incident_recommendations(incident_id);