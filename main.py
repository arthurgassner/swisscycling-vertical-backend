import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from pathlib import Path

RECORDS_FILEPATH = Path('records.csv')

# Create empty records if the records is empty.
if not RECORDS_FILEPATH.is_file():
    df = pd.DataFrame({
        'rank': pd.Series(dtype='int'),
        'name': pd.Series(dtype='string'),
        'datetime': pd.Series(dtype='datetime64[ns]'),
        'duration_s': pd.Series(dtype='int'),
    })
    df.to_csv(RECORDS_FILEPATH, index=False)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="[Swiss Cycling North-to-South Challenge] Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class Record(BaseModel):
    name: str
    datetime: str  # Use a string for simplicity; can be parsed to datetime later
    duration_s: int

@app.get("/")
async def get_root():
    logger.info(f"Received GET /")
    return {"message": "Welcome to the Swiss Cycling North-to-South Backend!"}

@app.get("/records")
async def get_records():
    logger.info("Received GET /records")

    # Load current records
    try:
        df = pd.read_csv(RECORDS_FILEPATH)
    except Exception as e:
        logger.error(f"Error loading records: {e}")
        raise HTTPException(status_code=500, detail="Error loading records.")
 
    return {"records": df.to_dict(orient='records')}

@app.get("/podium")
async def get_podium():
    logger.info(f"Received GET /podium")

    # Load current records
    try:
        df = pd.read_csv(RECORDS_FILEPATH)
    except Exception as e:
        logger.error(f"Error loading records: {e}")
        raise HTTPException(status_code=500, detail="Error loading records.")
    
    # Only keep the top 3
    df = df[df.rank <= 3]
 
    return {"podium": df.to_dict(orient='records')}

@app.post("/add-record")
async def post_add_record(record: Record):
    logger.info(f"Received POST /add-record with data: {record}")

    # Load current records
    try:
        df = pd.read_csv(RECORDS_FILEPATH)
    except Exception as e:
        logger.error(f"Error loading records: {e}")
        raise HTTPException(status_code=500, detail="Error loading records.")
 
    # Append new record
    new_record = {
        'name': record.name,
        'datetime': pd.to_datetime(record.datetime),
        'duration_s': record.duration_s
    }
    df = pd.concat([df, pd.DataFrame(new_record)], ignore_index=True)

    # Recompute ranks based on 'duration_s'
    df['rank'] = df['duration_s'].rank(method='min').astype(int)

    # Save the updated DataFrame back to CSV
    try:
        df.to_csv(RECORDS_FILEPATH, index=False)
    except Exception as e:
        logger.error("Error saving records: %s", e)
        raise HTTPException(status_code=500, detail="Error saving records")

    return {"message": "Record added successfully", "status": 200}

