import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Load CSV
df = pd.read_csv("../../Astram_event_data.csv")

# Rename only needed columns
column_mapping = {
    "veh_type": "vehicle_type"
}

df.rename(columns=column_mapping, inplace=True)

# Keep only DB-compatible columns
required_columns = [
    "event_type",
    "event_cause",
    "latitude",
    "longitude",
    "corridor",
    "zone",
    "junction",
    "address",
    "priority",
    "requires_road_closure",
    "vehicle_type",
    "start_datetime",
    "closed_datetime",
    "resolved_datetime",
    "status",
    "description"
]

df = df[required_columns]

df["priority"] = df["priority"].fillna("Medium")
df["event_type"] = df["event_type"].fillna("unknown")
df["event_cause"] = df["event_cause"].fillna("unknown")
df["status"] = df["status"].fillna("active")
df["requires_road_closure"] = df["requires_road_closure"].fillna(False)
df["vehicle_type"] = df["vehicle_type"].fillna("unknown")
# Insert into PostgreSQL
df.to_sql(
    "traffic_incidents",
    engine,
    if_exists="append",
    index=False
)

print(f"Inserted {len(df)} rows successfully.")