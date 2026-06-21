"""
Script to build FAISS index for RAG system
Run this after training the ML model

Usage:
    python build_rag_index.py --data-path data.csv
"""

import pandas as pd
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.retriever import RAGSystem

def build_faiss_index(data_path: str, output_dir: str = "models"):
    """
    Build FAISS index for historical incidents
    
    Args:
        data_path: Path to CSV file with incident data
        output_dir: Directory to save FAISS index
    """
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    print(f"Dataset shape: {df.shape}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize RAG system
    rag = RAGSystem()
    
    # Filter for closed/resolved incidents
    df_closed = df[df['status'].isin(['closed', 'resolved'])].copy()
    
    print(f"Processing {len(df_closed)} closed/resolved incidents...")
    
    # Prepare incident data
    incidents_list = []
    incident_ids = []
    
    for idx, row in df_closed.iterrows():
        incident_dict = {
            'event_type': row.get('event_type', 'unknown'),
            'event_cause': row.get('event_cause', 'unknown'),
            'corridor': row.get('corridor', 'unknown'),
            'zone': row.get('zone', 'unknown'),
            'priority': row.get('priority', 'Low'),
            'vehicle_type': row.get('veh_type', 'unknown'),
            'requires_road_closure': row.get('requires_road_closure', False),
        }
        
        # Calculate clearance time
        try:
            if pd.notna(row.get('closed_datetime')) and pd.notna(row.get('start_datetime')):
                start = pd.to_datetime(row['start_datetime'])
                closed = pd.to_datetime(row['closed_datetime'])
                clearance_time = (closed - start).total_seconds() / 60
                incident_dict['clearance_time'] = clearance_time
            else:
                incident_dict['clearance_time'] = None
        except:
            incident_dict['clearance_time'] = None
        
        incidents_list.append(incident_dict)
        incident_ids.append(idx)
    
    # Index incidents in batches
    batch_size = 100
    print("Indexing incidents...")
    
    for i in range(0, len(incidents_list), batch_size):
        batch_incidents = incidents_list[i:i+batch_size]
        batch_ids = incident_ids[i:i+batch_size]
        
        rag.index_batch(batch_incidents, batch_ids)
        print(f"Indexed {min(i+batch_size, len(incidents_list))}/{len(incidents_list)} incidents")
    
    # Save index
    print("Saving FAISS index...")
    rag.save(index_path=f'{output_dir}/faiss_index.pkl')
    
    print(f"\nFAISS index built successfully!")
    print(f"Total incidents indexed: {rag.get_index_size()}")
    print(f"Saved to: {output_dir}/faiss_index.pkl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS index for RAG")
    parser.add_argument(
        "--data-path",
        required=True,
        help="Path to incident CSV file"
    )
    parser.add_argument(
        "--output-dir",
        default="models",
        help="Directory to save FAISS index"
    )
    
    args = parser.parse_args()
    
    build_faiss_index(args.data_path, args.output_dir)
