-- Sample Data for TrafficTwin AI
-- Insert test data into database for demonstration

INSERT INTO traffic_incidents (
  event_type, event_cause, latitude, longitude, corridor, zone, junction,
  priority, requires_road_closure, vehicle_type, address,
  start_datetime, closed_datetime, status, actual_clearance_time_minutes
) VALUES

-- Vehicle Breakdowns
('unplanned', 'vehicle_breakdown', 13.0400041, 77.5180991, 'Tumkur Road', 'North Zone 1', 'JalahaliCross',
  'High', false, 'lcv', 'Tumkur Road, Jalahalli', 
  '2024-01-14 17:01:48', '2024-01-14 17:43:00', 'resolved', 42),

('unplanned', 'vehicle_breakdown', 13.0827, 77.5979, 'ORR North 1', 'North Zone 2', 'Nandini Layout Junc',
  'High', false, 'heavy_vehicle', 'ORR North, Hebbal',
  '2024-01-14 18:15:30', '2024-01-14 18:58:00', 'resolved', 43),

('unplanned', 'vehicle_breakdown', 12.9717, 77.6412, 'Bannerghata Road', 'South Zone 1', 'Mico Layout Junc',
  'Medium', false, 'bmtc_bus', 'Bannerghata Road, Jayanagar',
  '2024-01-14 19:20:15', '2024-01-14 20:02:00', 'resolved', 42),

-- Accidents
('unplanned', 'accident', 12.9667, 77.6615, 'ORR East 1', 'East Zone 1', 'Airport Road Junc',
  'High', true, 'private_car', 'ORR East, Jeevanbheema Nagar',
  '2024-01-14 17:45:20', '2024-01-14 18:35:00', 'resolved', 50),

('unplanned', 'accident', 13.0370, 77.6540, 'Old Madras Road', 'East Zone 2', 'Horamavu Junc',
  'Medium', false, 'private_car', 'Old Madras Road, Horamavu',
  '2024-01-14 20:10:45', '2024-01-14 21:15:00', 'resolved', 65),

-- Tree Falls
('unplanned', 'tree_fall', 12.9273, 77.5806, 'Non-corridor', 'South Zone 2', 'Vinayaka Circle',
  'Low', true, NULL, 'Jayanagar, 5th Main Road',
  '2024-01-14 19:45:16', '2024-01-15 02:33:00', 'resolved', 470),

('unplanned', 'tree_fall', 13.0061, 77.5794, 'Non-corridor', 'Central Zone', 'Bashyam Circle',
  'Low', false, NULL, 'Sankey Road, Sadashiva Nagar',
  '2024-01-14 17:56:55', '2024-01-14 22:15:00', 'resolved', 260),

-- Water Logging
('unplanned', 'water_logging', 13.0008, 77.6813, 'ORR East 2', 'East Zone 1', 'Whitefield Road Junc',
  'High', false, NULL, 'Whitefield Road, Data Center',
  '2024-01-14 18:01:40', '2024-01-15 01:50:00', 'resolved', 469),

-- Congestion
('unplanned', 'congestion', 13.0447, 77.5828, 'ORR North 2', 'North Zone 2', 'Bhadrapp Layout',
  'High', false, NULL, 'Outer Ring Road, RMV Stage 2',
  '2024-01-14 05:38:15', '2024-01-14 08:35:00', 'resolved', 177),

-- Pot Holes
('unplanned', 'pot_holes', 12.9169, 77.5950, 'Non-corridor', 'South Zone 1', 'East End Circle',
  'Low', false, NULL, 'South End Main Road, Jayanagar',
  '2024-01-14 22:35:41', '2024-01-15 06:48:00', 'resolved', 493),

-- Planned Event
('planned', 'public_event', 12.9788, 77.5995, 'CBD 2', 'Central Zone', 'Queens Statue Circle',
  'High', false, NULL, 'M Chinnaswamy Stadium, Cubbon Park',
  '2024-01-15 02:05:46', '2024-01-15 14:05:46', 'resolved', 720);

-- Insert sample predictions
INSERT INTO prediction_results (incident_id, predicted_clearance_time, peak_hour)
SELECT id, ROUND(actual_clearance_time_minutes * 0.95 + (RANDOM() * 5), 1), 
  CASE WHEN EXTRACT(HOUR FROM start_datetime) IN (7,8,9,16,17,18,19) THEN 1 ELSE 0 END
FROM traffic_incidents
WHERE actual_clearance_time_minutes IS NOT NULL;

-- Insert sample severity scores
INSERT INTO severity_scores (incident_id, severity_score, severity_level, 
  priority_weight, road_closure_weight, corridor_weight, vehicle_weight, peak_hour_weight, junction_weight)
VALUES
(1, 14.5, 'High', 8, 0, 2, 1.5, 2, 1),
(2, 15.0, 'High', 8, 0, 2.5, 2, 2, 0.5),
(3, 11.5, 'Medium', 5, 0, 2, 2, 2, 0.5),
(4, 16.0, 'High', 8, 3, 2, 0.5, 2, 0.5),
(5, 12.5, 'Medium', 5, 0, 2, 0.5, 2, 1),
(6, 5.0, 'Low', 2, 3, 0, 0, 0, 0),
(7, 4.5, 'Low', 2, 0, 0, 0, 0, 0),
(8, 14.0, 'High', 8, 0, 2, 0, 2, 2),
(9, 13.5, 'High', 8, 0, 2.5, 0, 2, 1),
(10, 3.0, 'Low', 2, 0, 0, 0, 0, 1),
(11, 14.0, 'High', 8, 0, 2.5, 0, 2, 1.5);

-- Insert sample recommendations
INSERT INTO incident_recommendations (incident_id, severity, predicted_clearance, 
  diversion_required, urgency_level, similar_cases_found, estimated_resolution_time)
SELECT id, 
  CASE WHEN severity_score < 7 THEN 'Low' WHEN severity_score < 13 THEN 'Medium' ELSE 'High' END,
  COALESCE((SELECT predicted_clearance_time FROM prediction_results pr WHERE pr.incident_id = traffic_incidents.id), 30),
  CASE WHEN severity_score > 12 THEN true ELSE false END,
  CASE WHEN severity_score > 12 THEN 'Critical' WHEN severity_score > 6 THEN 'High' ELSE 'Normal' END,
  FLOOR(RANDOM() * 5) + 3,
  COALESCE((SELECT predicted_clearance_time FROM prediction_results pr WHERE pr.incident_id = traffic_incidents.id), 30)
FROM traffic_incidents ti
JOIN severity_scores ss ON ti.id = ss.incident_id
WHERE ti.id <= 11;

-- Display inserted data
SELECT COUNT(*) as total_incidents FROM traffic_incidents;
SELECT COUNT(*) as total_predictions FROM prediction_results;
SELECT COUNT(*) as total_severity_scores FROM severity_scores;
SELECT COUNT(*) as total_recommendations FROM incident_recommendations;
