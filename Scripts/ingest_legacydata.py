from pathlib import Path
import pandas as pd
import urllib
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Resolve paths correctly for scripts/ingest_legaceydata.py
script_dir = Path(__file__).resolve().parent      # Points to the 'scripts' folder
project_root = script_dir.parent                  # Climbs 1 level up to 'Cold-chain-Logisitics-FDE'

load_dotenv(project_root / ".env")

# Check for the raw CSV dataset
data_path = project_root / "Data" / "Raw" / "dynamic_supply_chain_logistics_dataset.csv"

# Fallback check if the folder is lowercase or file is named differently
if not data_path.exists():
    data_path = project_root / "data" / "raw" / "dynamic_supply_chain_logistics_dataset.csv"

if not data_path.exists():
    raise FileNotFoundError(
        f"Could not find the dataset at {data_path}. "
        "Please confirm your CSV file is inside the Data/Raw (or data/raw) folder."
    )

db_host = os.getenv("SQL_SERVER_HOST", "localhost")
db_port = os.getenv("SQL_SERVER_PORT", "1433")
db_user = os.getenv("SQL_ADMIN_USER", "sa")
db_password = os.getenv("SQL_ADMIN_PASSWORD", "YourStrong@Passw0rd!")

# 1. Load the raw dataset
print(f"Loading CSV from {data_path}...")
df = pd.read_csv(data_path)

# 2. Map clean columns to the 2000s legacy enterprise schema
legacy_mapping = {
    'timestamp': 'TS_UTC',
    'vehicle_gps_latitude': 'V_LAT',
    'vehicle_gps_longitude': 'V_LON',
    'iot_temperature': 'IOT_TEMP_VAL_C',
    'cargo_condition_status': 'CGO_COND_CD',
    'risk_classification': 'RISK_CLS_TXT',
    'delay_probability': 'DELAY_PROB_DEC',
    'port_congestion_level': 'PRT_CNG_LVL',
    'route_risk_level': 'RT_RSK_IDX'
}

# Keep only the mapped columns and rename them
available_cols = [col for col in legacy_mapping.keys() if col in df.columns]
df_legacy = df[available_cols].rename(columns=legacy_mapping)

# Add legacy system ingestion tracking flag
df_legacy['SYS_INGEST_FLAG'] = 'Y'

# 3. Connect to Docker MSSQL Server
print("Connecting to legacy MSSQL Database...")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={db_host},{db_port};"
    f"DATABASE=master;"
    f"UID={db_user};"
    f"PWD={db_password};"
    f"Encrypt=no;"
    f"TrustServerCertificate=yes;"
)

params = urllib.parse.quote_plus(connection_string)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# 4. Ingest data into legacy table
table_name = 'TBL_SC_FLEET_HIST_RAW'
print(f"Ingesting into {table_name}. This may take a minute...")
df_legacy.to_sql(table_name, engine, if_exists='replace', index=False, schema='dbo')

print("Legacy data ingestion complete!") 