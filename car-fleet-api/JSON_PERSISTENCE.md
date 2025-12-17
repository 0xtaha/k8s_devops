# JSON Persistence Feature

## Overview

The Car Fleet API now includes JSON file persistence, allowing car data to be loaded from and automatically saved to a JSON file.

## Features

✅ **Load cars from JSON** - On startup, the application loads car data from `data/cars.json`  
✅ **Auto-save on modifications** - All changes (add, rent, return, delete) are automatically saved  
✅ **Persistent state** - Car data persists across application restarts  
✅ **Error handling** - Graceful handling of missing or invalid JSON files  

## File Structure

```
car-fleet-api/
└── data/
    ├── cars.json         # Runtime data (gitignored)
    └── cars.json.example # Template file (committed)
```

## JSON Format

```json
{
  "cars": [
    {
      "brand": "Renault",
      "model": "Clio",
      "year": 2022,
      "registration": "AB-123-CD",
      "availability": true
    }
  ]
}
```

## Service Layer Changes

### New Methods

**`load_from_json()`** - Load cars from JSON file
```python
success, error = rental_service.load_from_json()
```

**`save_to_json()`** - Save cars to JSON file
```python
success, error = rental_service.save_to_json()
```

### Auto-Save Operations

The following operations automatically save to JSON:
- ✓ `add_car()` - After adding a new car
- ✓ `rent_car()` - After renting a car
- ✓ `return_car()` - After returning a car
- ✓ `delete_car()` - After deleting a car

## Usage

### Starting the Application

```bash
# Copy example file on first run
cp data/cars.json.example data/cars.json

# Start the application
uv run python app.py
```

Output:
```
✓ Loaded 4 cars from data/cars.json
🚗 Car Fleet Management API Server
```

### Making Changes

All API operations automatically persist:

```bash
# Add a car (auto-saves to JSON)
curl -X POST http://localhost:5000/api/cars \
  -H "Content-Type: application/json" \
  -d '{"brand":"Toyota","model":"Camry","year":2023,"registration":"XYZ-123"}'

# Rent a car (auto-saves to JSON)
curl -X PUT http://localhost:5000/api/cars/XYZ-123/rent

# Restart application - data is preserved!
```

## Benefits

1. **Data Persistence** - Changes survive application restarts
2. **Simple Storage** - No database required for development
3. **Human-Readable** - Easy to edit JSON manually if needed
4. **Version Control** - Example file provides template
5. **Automatic** - No manual save required

## Configuration

The data file path can be configured when initializing the service:

```python
# Custom path
rental_service = CarsRentalService(agency, data_file="custom/path.json")

# Default path
rental_service = CarsRentalService(agency)  # Uses "data/cars.json"
```

## Error Handling

### Missing File

If `data/cars.json` doesn't exist on startup:
```
✗ Failed to load cars from JSON: Data file data/cars.json not found
Using empty fleet
```

The application continues with an empty fleet and will create the file on first modification.

### Invalid JSON

If the JSON file is malformed:
```
✗ Failed to load cars from JSON: Invalid JSON format: ...
Using empty fleet
```

## Testing

```bash
# Test JSON persistence
uv run python -c "
from src import Agency, CarsRentalService

agency = Agency('Test')
service = CarsRentalService(agency, 'data/cars.json')

# Load data
success, error = service.load_from_json()
print(f'Loaded: {len(service.get_all_cars())} cars')

# Add a car (auto-saves)
service.add_car('Toyota', 'Camry', 2023, 'XYZ-999')

# Verify persistence
service.load_from_json()
print(f'After reload: {len(service.get_all_cars())} cars')
"
```

## Git Configuration

Runtime data is excluded from version control:

```gitignore
# Runtime data
data/cars.json
```

The example file is committed:
```
data/cars.json.example  # Committed
data/cars.json          # Gitignored
```

## Future Enhancements

Potential improvements:
- 📝 Backup/restore functionality
- 🔄 JSON file validation on load
- 📊 Migration support for schema changes
- 🔒 File locking for concurrent access
- 💾 Database adapter for production use
