"""
CSV Upload API for bulk location data import
"""
import csv
import io
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import pandas as pd

from app.api.deps import get_current_admin_user
from app.models.user import UserModel
from app.services.kafka_producer import location_producer
from app.services.geo import geo_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class CSVUploadResponse(BaseModel):
    """Response model for CSV upload"""
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    message: str

# Expected CSV columns
REQUIRED_COLUMNS = ["city_name", "state", "latitude", "longitude"]
OPTIONAL_COLUMNS = [
    "pincode", "district", "is_metro", "is_capital", 
    "population", "area_sq_km", "alternate_names"
]

@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Upload a CSV file containing city data
    
    Expected CSV format:
    - city_name (required): Name of the city
    - state (required): State name
    - latitude (required): Latitude coordinate
    - longitude (required): Longitude coordinate
    - pincode (optional): Postal code (6 digits)
    - district (optional): District name
    - is_metro (optional): true/false
    - is_capital (optional): true/false
    - population (optional): Population count
    - area_sq_km (optional): Area in square kilometers
    - alternate_names (optional): Comma-separated alternative names
    
    Example CSV:
    ```
    city_name,state,latitude,longitude,pincode,district,is_metro,population
    Noida,Uttar Pradesh,28.5355,77.3910,201301,Gautam Buddha Nagar,false,642000
    ```
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read file content
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading CSV file: {str(e)}"
        )
    
    # Validate required columns
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    # Process rows
    valid_rows = 0
    invalid_rows = 0
    errors = []
    
    def process_csv_data():
        nonlocal valid_rows, invalid_rows
        
        for index, row in df.iterrows():
            try:
                # Prepare city data
                city_data = {
                    "event_type": "CREATE",
                    "city_name": str(row['city_name']).strip(),
                    "state": str(row['state']).strip(),
                    "latitude": float(row['latitude']),
                    "longitude": float(row['longitude']),
                    "source": f"csv_upload:user:{current_user.id}"
                }
                
                # Add optional fields
                if 'pincode' in row and pd.notna(row['pincode']):
                    city_data['pincode'] = str(int(row['pincode'])).zfill(6)
                
                if 'district' in row and pd.notna(row['district']):
                    city_data['district'] = str(row['district']).strip()
                
                if 'is_metro' in row and pd.notna(row['is_metro']):
                    city_data['is_metro'] = str(row['is_metro']).lower() in ['true', '1', 'yes']
                
                if 'is_capital' in row and pd.notna(row['is_capital']):
                    city_data['is_capital'] = str(row['is_capital']).lower() in ['true', '1', 'yes']
                
                if 'population' in row and pd.notna(row['population']):
                    city_data['population'] = int(row['population'])
                
                if 'area_sq_km' in row and pd.notna(row['area_sq_km']):
                    city_data['area_sq_km'] = float(row['area_sq_km'])
                
                if 'alternate_names' in row and pd.notna(row['alternate_names']):
                    city_data['alternate_names'] = [
                        name.strip() for name in str(row['alternate_names']).split(',')
                    ]
                
                # Validate coordinates
                if not (-90 <= city_data['latitude'] <= 90):
                    raise ValueError(f"Invalid latitude: {city_data['latitude']}")
                
                if not (-180 <= city_data['longitude'] <= 180):
                    raise ValueError(f"Invalid longitude: {city_data['longitude']}")
                
                # Produce to Kafka
                success = location_producer.produce_location_update(**city_data)
                
                if success:
                    valid_rows += 1
                else:
                    invalid_rows += 1
                    errors.append({
                        "row": index + 2,  # +2 for header and 0-based index
                        "city": city_data['city_name'],
                        "error": "Failed to publish to Kafka"
                    })
                    
            except Exception as e:
                invalid_rows += 1
                errors.append({
                    "row": index + 2,
                    "city": row.get('city_name', 'Unknown'),
                    "error": str(e)
                })
        
        # Flush Kafka producer
        location_producer.flush()
    
    # Process in background
    background_tasks.add_task(process_csv_data)
    
    total_rows = len(df)
    
    return CSVUploadResponse(
        total_rows=total_rows,
        valid_rows=valid_rows,
        invalid_rows=invalid_rows,
        errors=errors[:10],  # Limit errors to first 10
        message=f"CSV upload initiated. Processing {total_rows} rows in background."
    )

@router.post("/upload-direct", response_model=CSVUploadResponse)
async def upload_csv_direct(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Upload a CSV file and directly save to MongoDB (bypassing Kafka)
    
    Use this for immediate imports when Kafka is not available.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read file content
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading CSV file: {str(e)}"
        )
    
    # Validate required columns
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    # Process rows directly
    valid_rows = 0
    invalid_rows = 0
    errors = []
    cities_to_add = []
    
    for index, row in df.iterrows():
        try:
            # Prepare city data
            city_data = {
                "name": str(row['city_name']).strip(),
                "state": str(row['state']).strip(),
                "latitude": float(row['latitude']),
                "longitude": float(row['longitude']),
                "is_popular": False
            }
            
            # Add optional fields
            if 'is_metro' in row and pd.notna(row['is_metro']):
                is_metro = str(row['is_metro']).lower() in ['true', '1', 'yes']
                city_data['is_popular'] = is_metro  # Popular if metro
            
            # Validate coordinates
            if not (-90 <= city_data['latitude'] <= 90):
                raise ValueError(f"Invalid latitude: {city_data['latitude']}")
            
            if not (-180 <= city_data['longitude'] <= 180):
                raise ValueError(f"Invalid longitude: {city_data['longitude']}")
            
            cities_to_add.append(city_data)
            valid_rows += 1
            
        except Exception as e:
            invalid_rows += 1
            errors.append({
                "row": index + 2,
                "city": row.get('city_name', 'Unknown'),
                "error": str(e)
            })
    
    # Save to database
    if cities_to_add:
        try:
            # Use geo_service to add cities
            for city in cities_to_add:
                existing = await geo_service._get_city_from_db(city['name'], city['state'])
                if not existing:
                    await geo_service.db.cities.insert_one(city)
            
            logger.info(f"Imported {len(cities_to_add)} cities from CSV")
        except Exception as e:
            logger.error(f"Database error during CSV import: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save cities to database"
            )
    
    return CSVUploadResponse(
        total_rows=len(df),
        valid_rows=valid_rows,
        invalid_rows=invalid_rows,
        errors=errors[:10],
        message=f"Successfully imported {valid_rows} cities directly to database."
    )

@router.get("/template")
async def download_csv_template():
    """
    Download a CSV template for city data upload
    """
    # Create template CSV
    template_data = [
        {
            "city_name": "Example City",
            "state": "Example State",
            "latitude": 25.0000,
            "longitude": 75.0000,
            "pincode": "123456",
            "district": "Example District",
            "is_metro": "false",
            "is_capital": "false",
            "population": 100000,
            "area_sq_km": 50.5,
            "alternate_names": "Alt Name 1,Alt Name 2"
        }
    ]
    
    # Convert to CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=template_data[0].keys())
    writer.writeheader()
    writer.writerows(template_data)
    
    return {
        "filename": "city_upload_template.csv",
        "content": output.getvalue(),
        "instructions": {
            "required_fields": REQUIRED_COLUMNS,
            "optional_fields": OPTIONAL_COLUMNS,
            "boolean_fields": ["is_metro", "is_capital"],
            "boolean_values": "true/false, yes/no, 1/0",
            "alternate_names": "Comma-separated values",
            "pincode": "6-digit number"
        }
    }
