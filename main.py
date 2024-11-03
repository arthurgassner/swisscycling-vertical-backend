import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from datetime import datetime

RECORDS_FILEPATH = Path('data/records.csv')

# Create empty records if the records is empty.
if not RECORDS_FILEPATH.is_file():
    df = pd.DataFrame({
        'rank': pd.Series(dtype='int'),
        'name': pd.Series(dtype='string'),
        'datetime': pd.Series(dtype='datetime64[ns]'),
        'duration_s': pd.Series(dtype='int'),
        'avatar_url': pd.Series(dtype='string'),
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
    """Get all the records saved on disk.

    Raises:
        HTTPException: 500 error if there is an issue loading the records.
    """
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
    """Get the records whose rank is 1,2,3.

    Raises:
        HTTPException: 500 error if there is an issue loading the records.
    """
    logger.info(f"Received GET /podium")

    # Load current records
    try:
        df = pd.read_csv(RECORDS_FILEPATH)
    except Exception as e:
        logger.error(f"Error loading records: {e}")
        raise HTTPException(status_code=500, detail="Error loading records.")
    
    # Only keep the top 3
    df = df[df["rank"] <= 3]
 
    return {"podium": df.to_dict(orient='records')}

@app.get("/add-dummy-records")
async def get_add_dummy_records():
    """Add 5 dummy records, meant for testing.

    Raises:
        HTTPException: 500 error if there is an issue loading the records.
        HTTPException: 500 if there is an issue dumping the records to disk.
    """
    logger.info(f"Received GET /add-dummy-records")

    # Load current records
    try:
        df = pd.read_csv(RECORDS_FILEPATH)
    except Exception as e:
        logger.error(f"Error loading records: {e}")
        raise HTTPException(status_code=500, detail="Error loading records.")
    
    SOME_AVATAR_URL = "https://avatars.githubusercontent.com/u/38256417"
    dummy_df = pd.DataFrame({
        "name": ["This could be you", "This could also be you!", "You again, maybe", "Maybe you tomorrow?", "A you within reach"],
        "datetime": [datetime(2020, 10, 31), datetime(2023, 1, 1), datetime(1997, 7, 25), datetime(2017, 8, 30), datetime(2019, 8, 30)],
        "duration_s": [60000, 50000, 72300, 30044, 80000],
        "avatar_url": [SOME_AVATAR_URL] * 5
    })
    df = pd.concat([df,dummy_df], ignore_index=True)

    # Recompute ranks based on 'duration_s'
    df['rank'] = df['duration_s'].rank(method='min').astype(int)
    df = df.sort_values(by='rank')

    # Save the updated DataFrame back to CSV
    try:
        df.to_csv(RECORDS_FILEPATH, index=False)
    except Exception as e:
        logger.error("Error saving records: %s", e)
        raise HTTPException(status_code=500, detail="Error saving records")

    return {"message": "Record added successfully", "status": 200}

@app.post("/add-record")
async def post_add_record(record: Record):
    """Add the record to the list of record saved on disk.

    Args:
        record (Record): Record to be added.

    Raises:
        HTTPException: 500 if there is an issue loading the records from disk.
        HTTPException: 500 if there is an issue dumping the records to disk.
    """
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
        'duration_s': record.duration_s,
        'avatar_url': pd.Series(dtype='string'),
    }
    df = pd.concat([df, pd.DataFrame(new_record)], ignore_index=True)

    # Recompute ranks based on 'duration_s'
    df['rank'] = df['duration_s'].rank(method='min').astype(int)
    df = df.sort_values(by='rank')

    # Save the updated DataFrame back to CSV
    try:
        df.to_csv(RECORDS_FILEPATH, index=False)
    except Exception as e:
        logger.error("Error saving records: %s", e)
        raise HTTPException(status_code=500, detail="Error saving records")

    return {"message": "Record added successfully", "status": 200}

