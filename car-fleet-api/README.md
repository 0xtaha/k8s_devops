# Car Fleet API

A RESTful API for managing a car rental fleet, built with Flask and following Clean Architecture principles.

## Features

- ✅ Add, retrieve, update, and delete cars
- ✅ Rent and return cars
- ✅ Get fleet statistics
- ✅ **JSON file persistence** - Data persists across restarts
- ✅ Clean Architecture (4-layer design)
- ✅ Type hints throughout
- ✅ RESTful API design

## Quick Start

```bash
# Install dependencies
uv sync

# Copy example data file (first time only)
cp data/cars.json.example data/cars.json

# Run the application
uv run python app.py

# Access API at http://localhost:5000
```

The application loads car data from `data/cars.json` on startup and automatically saves all changes.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/api/cars` | Get all cars |
| GET | `/api/cars/available` | Get available cars |
| GET | `/api/cars/<registration>` | Get specific car |
| POST | `/api/cars` | Add new car |
| PUT | `/api/cars/<registration>/rent` | Rent a car |
| PUT | `/api/cars/<registration>/return` | Return a car |
| DELETE | `/api/cars/<registration>` | Delete a car |
| GET | `/api/stats` | Get fleet statistics |

## Architecture

This project follows **Clean Architecture** with clear separation of concerns:

```
Routes (app.py)
    ↓
Controller (controller.py) ← HTTP handling
    ↓
Service (service.py)       ← Business logic
    ↓
Models (car.py, agency.py) ← Data entities
```

### Project Structure

```
car-fleet-api/
├── car_fleet/
│   ├── car.py         # Car model
│   ├── agency.py      # Agency model
│   ├── service.py     # CarsRentalService (business logic)
│   └── controller.py  # RentalController (HTTP handling)
├── app.py             # Flask routes
├── pyproject.toml     # UV configuration
└── Dockerfile         # Container with UV
```

## Example Usage

### Get All Cars
```bash
curl http://localhost:5000/api/cars
```

### Add a Car
```bash
curl -X POST http://localhost:5000/api/cars \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Toyota",
    "model": "Camry",
    "year": 2023,
    "registration": "ABC-123"
  }'
```

### Rent a Car
```bash
curl -X PUT http://localhost:5000/api/cars/ABC-123/rent
```

### Return a Car
```bash
curl -X PUT http://localhost:5000/api/cars/ABC-123/return
```

### Get Statistics
```bash
curl http://localhost:5000/api/stats
```

## Development

### Install Dependencies
```bash
uv sync
```

### Run Application
```bash
uv run python app.py
```

### Build Docker Image
```bash
docker build -t car-fleet-api:latest .
```

### Run Container
```bash
docker run -p 5000:5000 car-fleet-api:latest
```

## Architecture Details

For complete architecture documentation, see [ARCHITECTURE_SUMMARY.md](./ARCHITECTURE_SUMMARY.md).

### Layer Responsibilities

**Routes (app.py)**: URL mapping and delegation  
**Controller (controller.py)**: HTTP requests/responses, JSON formatting  
**Service (service.py)**: Business logic, data validation  
**Models (car.py, agency.py)**: Data entities

### Design Patterns

- MVC (Model-View-Controller)
- Service Layer Pattern
- Dependency Injection
- Repository Pattern

## Testing

```bash
# Test service layer
uv run python -c "from car_fleet import CarsRentalService, Agency; \
  service = CarsRentalService(Agency('Test')); \
  success, car, _ = service.add_car('Toyota', 'Camry', 2023, 'XYZ-123'); \
  print('✓ Service works!' if success else '✗ Failed')"

# Test controller layer
uv run python -c "from flask import Flask; \
  from car_fleet import RentalController, CarsRentalService, Agency; \
  app = Flask(__name__); \
  with app.app_context(): \
    controller = RentalController(CarsRentalService(Agency('Test'))); \
    response, status = controller.get_all_cars(); \
    print(f'✓ Controller works! Status: {status}')"
```

## Dependencies

- Flask >= 3.0.0 - Web framework
- flask-cors >= 4.0.0 - CORS support

Managed with **UV** for fast, reliable dependency management.

## License

Part of Orange DevOps Task - Python Programming Exercise
