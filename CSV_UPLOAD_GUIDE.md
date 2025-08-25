# CSV Upload Guide - City Data Management

## Overview

You can now upload city data in bulk using CSV files through multiple interfaces:

1. **Web UI** - Beautiful drag-and-drop interface
2. **Admin Panel** - Integrated into the app
3. **API** - Direct API endpoints

## CSV File Format

### Required Fields
- `city_name` - Name of the city
- `state` - State name
- `latitude` - Latitude coordinate (-90 to 90)
- `longitude` - Longitude coordinate (-180 to 180)

### Optional Fields
- `pincode` - 6-digit postal code
- `district` - District name
- `is_metro` - true/false
- `is_capital` - true/false
- `population` - Population count
- `area_sq_km` - Area in square kilometers
- `alternate_names` - Comma-separated alternative names

### Example CSV
```csv
city_name,state,latitude,longitude,pincode,district,is_metro,is_capital,population,area_sq_km,alternate_names
Mumbai,Maharashtra,19.0760,72.8777,400001,Mumbai,true,false,20411000,603.4,"Bombay"
Delhi,Delhi,28.6139,77.2090,110001,New Delhi,true,true,32941000,1484,"New Delhi,NCR"
```

## Upload Methods

### 1. Web UI (Standalone)
Open `csv-upload-ui.html` in your browser:
```bash
open csv-upload-ui.html
```

**Note**: You need to set your admin auth token:
```javascript
// In browser console
localStorage.setItem('authToken', 'YOUR_ADMIN_TOKEN');
```

### 2. Admin Panel (In-App)
1. Login as admin
2. Navigate to: http://localhost:3000/admin/csv-upload
3. Drag and drop your CSV file
4. Choose upload method:
   - **Direct Import** - Saves directly to MongoDB (recommended)
   - **Via Kafka** - Uses event streaming (requires Kafka running)

### 3. API Endpoints

#### Direct Upload (No Kafka Required)
```bash
curl -X POST http://localhost:8000/api/v1/csv-upload/upload-direct \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@your_cities.csv"
```

#### Kafka Upload (Event Streaming)
```bash
# First, ensure Kafka is running
docker-compose -f kafka-docker-compose.yml up -d

# Upload via Kafka
curl -X POST http://localhost:8000/api/v1/csv-upload/upload \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@your_cities.csv"
```

## Sample Files Provided

1. **Template CSV** - Basic structure with one example
   - Download via UI or API: `/api/v1/csv-upload/template`

2. **Sample Indian Cities** - 50 major Indian cities
   - File: `sample_indian_cities.csv`
   - Includes all state capitals and major cities

## Testing the Upload

### Quick Test with Sample Data
```bash
# Using the provided sample file
curl -X POST http://localhost:8000/api/v1/csv-upload/upload-direct \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample_indian_cities.csv"
```

### Expected Response
```json
{
  "total_rows": 50,
  "valid_rows": 50,
  "invalid_rows": 0,
  "errors": [],
  "message": "Successfully imported 50 cities directly to database."
}
```

## Error Handling

The system validates:
- Required fields presence
- Coordinate ranges
- Pincode format (6 digits)
- Boolean values (true/false, yes/no, 1/0)

Errors are reported with:
- Row number
- City name
- Error description

## Best Practices

1. **Start Small** - Test with a few rows first
2. **Validate Coordinates** - Ensure lat/long are accurate
3. **Use UTF-8 Encoding** - For city names with special characters
4. **Check Duplicates** - System will skip existing cities
5. **Boolean Values** - Use lowercase: true/false

## Troubleshooting

### Common Issues

1. **"Missing required columns"**
   - Ensure your CSV has all 4 required fields
   - Check column names match exactly

2. **"Invalid latitude/longitude"**
   - Latitude: -90 to 90
   - Longitude: -180 to 180

3. **"Authentication failed"**
   - Ensure you're logged in as admin
   - Check your auth token is valid

4. **Kafka errors**
   - Ensure Kafka is running
   - Check Kafka UI at http://localhost:8080

## Next Steps

After uploading cities:
1. Verify in MongoDB: Cities collection
2. Test distance calculations
3. Check city search functionality
4. Monitor Kafka topics (if using Kafka)

## Support

For issues or questions:
- Check backend logs: `backend/logs/`
- Kafka UI: http://localhost:8080
- MongoDB: Check cities collection
