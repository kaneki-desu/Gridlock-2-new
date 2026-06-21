from typing import Dict, Tuple

class SeverityEngine:
    """
    Rule-based severity calculation engine for traffic incidents
    """
    
    # Weight configurations
    PRIORITY_WEIGHTS = {
        'Low': 2,
        'Medium': 5,
        'High': 8
    }
    
    ROAD_CLOSURE_WEIGHT = 3
    
    CORRIDOR_WEIGHTS = {
        'Tumkur Road': 2,
        'ORR North 1': 2.5,
        'ORR North 2': 2.5,
        'ORR East 1': 2,
        'ORR East 2': 2,
        'ORR West 1': 2,
        'Bellary Road 1': 2,
        'Bellary Road 2': 2,
        'Bannerghata Road': 2,
        'Hosur Road': 2,
        'Magadi Road': 1.5,
        'Old Madras Road': 2,
        'CBD 2': 2.5,
        'Non-corridor': 1
    }
    
    VEHICLE_WEIGHTS = {
        'heavy_vehicle': 2,
        'bmtc_bus': 2.5,
        'ksrtc_bus': 2.5,
        'private_bus': 2,
        'private_car': 0.5,
        'lcv': 1.5,
        'unknown': 1
    }
    
    @classmethod
    def calculate_severity(cls, incident_dict: Dict) -> Tuple[float, str]:
        """
        Calculate severity score and level for an incident
        
        Args:
            incident_dict: Dictionary with incident details
        
        Returns:
            Tuple of (severity_score, severity_level)
        """
        
        score = 0
        weights = {}
        
        # Priority weight
        priority = incident_dict.get('priority', 'Low')
        priority_weight = cls.PRIORITY_WEIGHTS.get(priority, 2)
        score += priority_weight
        weights['priority_weight'] = priority_weight
        
        # Road closure weight
        requires_closure = incident_dict.get('requires_road_closure', False)
        closure_weight = cls.ROAD_CLOSURE_WEIGHT if requires_closure else 0
        score += closure_weight
        weights['road_closure_weight'] = closure_weight
        
        # Corridor weight
        corridor = incident_dict.get('corridor', 'Non-corridor')
        corridor_weight = cls.CORRIDOR_WEIGHTS.get(corridor, 1)
        score += corridor_weight
        weights['corridor_weight'] = corridor_weight
        
        # Vehicle weight
        vehicle_type = incident_dict.get('vehicle_type', 'unknown')
        vehicle_weight = cls.VEHICLE_WEIGHTS.get(vehicle_type, 1)
        score += vehicle_weight
        weights['vehicle_weight'] = vehicle_weight
        
        # Peak hour weight
        peak_hour = incident_dict.get('peak_hour', 0)
        peak_weight = 2 if peak_hour else 0
        score += peak_weight
        weights['peak_hour_weight'] = peak_weight
        
        # Junction type weight
        junction = incident_dict.get('junction', None)
        junction_weight = 1.5 if junction else 0
        score += junction_weight
        weights['junction_weight'] = junction_weight
        
        # Determine severity level
        severity_level = cls._get_severity_level(score)
        
        return score, severity_level, weights
    
    @classmethod
    def _get_severity_level(cls, score: float) -> str:
        """
        Determine severity level based on score
        
        Score ranges:
        0-6 → Low
        7-12 → Medium
        13+ → High
        """
        if score < 7:
            return "Low"
        elif score < 13:
            return "Medium"
        else:
            return "High"
    
    @classmethod
    def calculate_urgency_level(cls, severity_level: str, clearance_time: float) -> str:
        """
        Calculate urgency level based on severity and predicted clearance time
        
        Args:
            severity_level: Severity level (Low/Medium/High)
            clearance_time: Predicted clearance time in minutes
        
        Returns:
            Urgency level string
        """
        if severity_level == "High" or clearance_time > 60:
            return "Critical"
        elif severity_level == "Medium" or clearance_time > 30:
            return "High"
        else:
            return "Normal"
