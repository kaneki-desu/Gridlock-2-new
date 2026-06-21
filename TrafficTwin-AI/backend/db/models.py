from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index, TIMESTAMP
from sqlalchemy.sql import func
from db.database import Base
from datetime import datetime

class TrafficIncident(Base):
    """
    Traffic incident model - stores all incident information
    """
    __tablename__ = "traffic_incidents"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Incident Details
    event_type = Column(String(50), nullable=False, index=True)  # planned/unplanned
    event_cause = Column(String(100), nullable=False, index=True)
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    corridor = Column(String(100), nullable=True, index=True)
    zone = Column(String(100), nullable=True)
    junction = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Incident Attributes
    priority = Column(String(20), nullable=False, index=True)  # Low/Medium/High
    requires_road_closure = Column(Boolean, default=False)
    vehicle_type = Column(String(50), nullable=True)
    
    # Timestamps
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    closed_datetime = Column(DateTime(timezone=True), nullable=True)
    resolved_datetime = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    # Status
    status = Column(String(20), default="active", index=True)  # active/closed/resolved
    
    # Resolution Details
    actual_clearance_time_minutes = Column(Integer, nullable=True)  # calculated
    description = Column(Text, nullable=True)
    
    # For RAG storage
    has_embedding = Column(Boolean, default=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_incident_coordinates', 'latitude', 'longitude'),
        Index('ix_incident_time_range', 'start_datetime', 'closed_datetime'),
    )

    def __repr__(self):
        return f"<TrafficIncident(id={self.id}, event_type={self.event_type}, status={self.status})>"


class PredictionResult(Base):
    """
    Stores ML predictions for incidents
    """
    __tablename__ = "prediction_results"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False, index=True)
    
    # XGBoost prediction
    predicted_clearance_time = Column(Float, nullable=False)
    
    # Features used
    peak_hour = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class SeverityScore(Base):
    """
    Stores severity calculations for incidents
    """
    __tablename__ = "severity_scores"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False, index=True)
    
    # Severity metrics
    severity_score = Column(Float, nullable=False)
    severity_level = Column(String(20), nullable=False, index=True)  # Low/Medium/High
    
    # Component weights
    priority_weight = Column(Float)
    road_closure_weight = Column(Float)
    corridor_weight = Column(Float)
    vehicle_weight = Column(Float)
    peak_hour_weight = Column(Float)
    junction_weight = Column(Float)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class SimilarIncident(Base):
    """
    Stores relationships between similar incidents for RAG
    """
    __tablename__ = "similar_incidents"

    id = Column(Integer, primary_key=True, index=True)
    query_incident_id = Column(Integer, nullable=False, index=True)
    similar_incident_id = Column(Integer, nullable=False, index=True)
    
    # Similarity metrics
    similarity_score = Column(Float, nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class IncidentRecommendation(Base):
    """
    Stores recommendations generated for incidents
    """
    __tablename__ = "incident_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False, index=True)
    
    # Recommendation details
    severity = Column(String(20), nullable=False)
    predicted_clearance = Column(Float, nullable=False)
    diversion_required = Column(Boolean, default=False)
    urgency_level = Column(String(20), nullable=False)
    similar_cases_found = Column(Integer, default=0)
    estimated_resolution_time = Column(Float, nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
