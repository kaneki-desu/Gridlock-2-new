from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from db import get_db, TrafficIncident, PredictionResult, SeverityScore, IncidentRecommendation
from ml.preprocessor import ClearanceTimePredictor
from rag.retriever import RAGSystem
from severity.engine import SeverityEngine
from llm.groq_client import get_llm_suggestions

# Pydantic schemas
class IncidentInput(BaseModel):
    event_type: str  # planned/unplanned
    event_cause: str
    latitude: float
    longitude: float
    corridor: Optional[str] = None
    zone: Optional[str] = None
    junction: Optional[str] = None
    priority: str  # Low/Medium/High
    requires_road_closure: bool = False
    vehicle_type: Optional[str] = None
    address: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "unplanned",
                "event_cause": "vehicle_breakdown",
                "latitude": 13.0400041,
                "longitude": 77.5180991,
                "corridor": "Tumkur Road",
                "zone": "North Zone 1",
                "junction": "JalahaliCross",
                "priority": "High",
                "requires_road_closure": False,
                "vehicle_type": "lcv",
                "address": "Tumkur Road, Bengaluru"
            }
        }


class ClearancePredictionResponse(BaseModel):
    predicted_clearance_time: float
    confidence: str


class SeverityResponse(BaseModel):
    severity_score: float
    severity_level: str


class SimilarIncidentResponse(BaseModel):
    incident_id: int
    similarity_score: float
    summary: str


class RecommendationResponse(BaseModel):
    severity: str
    predicted_clearance: float
    diversion_required: bool
    urgency_level: str
    similar_cases_found: int
    estimated_resolution_time: float
    llm_suggestions: Optional[str] = None


router = APIRouter()

# Global instances (in production, use dependency injection)
predictor = ClearanceTimePredictor()
rag_system = RAGSystem()

try:
    predictor.load_model('models/xgboost_model.pkl')
    rag_system.load('models/faiss_index.pkl')
except:
    print("Models not found. Please train them first using training scripts.")


@router.post("/incident", response_model=dict)
def submit_incident(
    incident: IncidentInput,
    db: Session = Depends(get_db)
):
    """
    Submit a new traffic incident
    
    This endpoint:
    1. Stores incident in PostgreSQL
    2. Generates predictions
    3. Calculates severity
    4. Retrieves similar incidents
    5. Generates recommendations
    """
    try:
        # Create database record
        db_incident = TrafficIncident(
            event_type=incident.event_type,
            event_cause=incident.event_cause,
            latitude=incident.latitude,
            longitude=incident.longitude,
            corridor=incident.corridor or "Unknown",
            zone=incident.zone,
            junction=incident.junction,
            priority=incident.priority,
            requires_road_closure=incident.requires_road_closure,
            vehicle_type=incident.vehicle_type or "unknown",
            address=incident.address,
            start_datetime=datetime.utcnow(),
            status="active"
        )
        
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)
        incident_id = db_incident.id
        
        # Prepare feature dict for ML
        feature_dict = {
            'event_type': incident.event_type,
            'event_cause': incident.event_cause,
            'latitude': incident.latitude,
            'longitude': incident.longitude,
            'corridor': incident.corridor or "Unknown",
            'priority': incident.priority,
            'requires_road_closure': incident.requires_road_closure,
            'vehicle_type': incident.vehicle_type or "unknown",
            'junction': incident.junction or "Unknown",
            'peak_hour': datetime.utcnow().hour
        }
        
        # Predict clearance time
        predicted_clearance = predictor.predict(feature_dict)
        
        # Store prediction
        prediction = PredictionResult(
            incident_id=incident_id,
            predicted_clearance_time=predicted_clearance
        )
        db.add(prediction)
        db.commit()
        
        # Calculate severity
        incident_dict = incident.dict()
        incident_dict['peak_hour'] = 0
        severity_score, severity_level, weights = SeverityEngine.calculate_severity(incident_dict)
        
        # Store severity
        severity = SeverityScore(
            incident_id=incident_id,
            severity_score=severity_score,
            severity_level=severity_level,
            **weights
        )
        db.add(severity)
        db.commit()
        
        # Retrieve similar incidents
        similar = rag_system.retrieve_similar(incident_dict, k=5)
        
        # Calculate recommendations
        urgency = SeverityEngine.calculate_urgency_level(severity_level, predicted_clearance)
        diversion_required = severity_level == "High" or predicted_clearance > 30
        
        recommendation = IncidentRecommendation(
            incident_id=incident_id,
            severity=severity_level,
            predicted_clearance=predicted_clearance,
            diversion_required=diversion_required,
            urgency_level=urgency,
            similar_cases_found=len(similar),
            estimated_resolution_time=predicted_clearance
        )
        db.add(recommendation)
        db.commit()

        llm_suggestions = get_llm_suggestions(
            current_incident=incident_dict,
            recommendation={
                "severity": severity_level,
                "predicted_clearance": round(predicted_clearance, 2),
                "diversion_required": diversion_required,
                "urgency_level": urgency,
                "estimated_resolution_time": round(predicted_clearance, 2),
            },
            similar_incidents=similar[:3]
        )
        
        return {
            "incident_id": incident_id,
            "status": "created",
            "severity": severity_level,
            "predicted_clearance": round(predicted_clearance, 2),
            "diversion_required": diversion_required,
            "urgency_level": urgency,
            "similar_cases_found": len(similar),
            "llm_suggestions": llm_suggestions
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating incident: {str(e)}"
        )


@router.post("/predict-clearance", response_model=ClearancePredictionResponse)
def predict_clearance(incident: IncidentInput):
    """
    Predict clearance time for an incident
    """
    try:
        feature_dict = {
            'event_type': incident.event_type,
            'event_cause': incident.event_cause,
            'latitude': incident.latitude,
            'longitude': incident.longitude,
            'corridor': incident.corridor or "Unknown",
            'priority': incident.priority,
            'requires_road_closure': incident.requires_road_closure,
            'vehicle_type': incident.vehicle_type or "unknown",
            'junction': incident.junction or "Unknown",
            'peak_hour': datetime.utcnow().hour
        }
        print(feature_dict)
        prediction = predictor.predict(feature_dict)
        print("\n",prediction)
        # Determine confidence level
        if prediction < 15:
            confidence = "High"
        elif prediction < 45:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return {
            "predicted_clearance_time": round(prediction, 2),
            "confidence": confidence
            
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction error: {str(e)}"
        )


@router.post("/calculate-severity", response_model=SeverityResponse)
def calculate_severity(incident: IncidentInput):
    """
    Calculate severity score for an incident
    """
    try:
        incident_dict = incident.dict()
        incident_dict['peak_hour'] = 0
        
        severity_score, severity_level, _ = SeverityEngine.calculate_severity(incident_dict)
        
        return {
            "severity_score": round(severity_score, 2),
            "severity_level": severity_level
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Severity calculation error: {str(e)}"
        )


@router.post("/retrieve-similar", response_model=List[SimilarIncidentResponse])
def retrieve_similar(incident: IncidentInput):
    """
    Retrieve similar historical incidents using RAG
    """
    try:
        incident_dict = incident.dict()
        similar_incidents = rag_system.retrieve_similar(incident_dict, k=5)
        
        return similar_incidents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Retrieval error: {str(e)}"
        )


@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(incident: IncidentInput):
    """
    Get complete recommendation based on all components
    """
    try:
        # Get predictions
        feature_dict = {
            'event_type': incident.event_type,
            'event_cause': incident.event_cause,
            'latitude': incident.latitude,
            'longitude': incident.longitude,
            'corridor': incident.corridor or "Unknown",
            'priority': incident.priority,
            'requires_road_closure': incident.requires_road_closure,
            'vehicle_type': incident.vehicle_type or "unknown",
            'junction': incident.junction or "Unknown",
            'peak_hour': datetime.utcnow().hour
        }
                
        predicted_clearance = predictor.predict(feature_dict)
        
        # Get severity
        incident_dict = incident.dict()
        incident_dict['peak_hour'] = 0
        severity_score, severity_level, _ = SeverityEngine.calculate_severity(incident_dict)
        
        # Get similar cases
        similar_incidents = rag_system.retrieve_similar(incident_dict, k=5)
        
        # Generate recommendations
        urgency = SeverityEngine.calculate_urgency_level(severity_level, predicted_clearance)
        diversion_required = severity_level == "High" or predicted_clearance > 30

        llm_suggestions = get_llm_suggestions(
            current_incident=incident_dict,
            recommendation={
                "severity": severity_level,
                "predicted_clearance": round(predicted_clearance, 2),
                "diversion_required": diversion_required,
                "urgency_level": urgency,
                "estimated_resolution_time": round(predicted_clearance, 2),
            },
            similar_incidents=similar_incidents[:3]
        )
        
        return {
            "severity": severity_level,
            "predicted_clearance": round(predicted_clearance, 2),
            "diversion_required": diversion_required,
            "urgency_level": urgency,
            "similar_cases_found": len(similar_incidents),
            "estimated_resolution_time": round(predicted_clearance, 2),
            "llm_suggestions": llm_suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recommendation error: {str(e)}"
        )


@router.post("/resolve-incident/{incident_id}")
def resolve_incident(
    incident_id: int,
    actual_clearance_time: int,
    db: Session = Depends(get_db)
):
    """
    Resolve an incident and update learning systems
    
    This endpoint:
    1. Updates incident status
    2. Records actual clearance time
    3. Generates summary
    4. Updates RAG system
    """
    try:
        incident = db.query(TrafficIncident).filter(
            TrafficIncident.id == incident_id
        ).first()
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        
        # Update incident
        incident.status = "resolved"
        incident.closed_datetime = datetime.utcnow()
        incident.actual_clearance_time_minutes = actual_clearance_time
        
        db.commit()
        db.refresh(incident)
        
        # Update RAG with resolved incident
        incident_dict = {
            'event_type': incident.event_type,
            'event_cause': incident.event_cause,
            'corridor': incident.corridor,
            'zone': incident.zone,
            'priority': incident.priority,
            'vehicle_type': incident.vehicle_type,
            'clearance_time': actual_clearance_time
        }
        
        rag_system.index_incident(incident_dict, incident_id)
        
        return {
            "incident_id": incident_id,
            "status": "resolved",
            "actual_clearance_time": actual_clearance_time,
            "message": "Incident resolved and learning systems updated"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error resolving incident: {str(e)}"
        )


@router.get("/incident/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Get incident details
    """
    incident = db.query(TrafficIncident).filter(
        TrafficIncident.id == incident_id
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    
    return incident


@router.get("/incidents")
def list_incidents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all incidents with optional filtering
    """
    query = db.query(TrafficIncident)
    
    if status:
        query = query.filter(TrafficIncident.status == status)
    
    incidents = query.offset(skip).limit(limit).all()
    
    return incidents
