# Car Fleet API - Architecture Summary

## Complete Architecture

The Car Fleet Management API now follows **Clean Architecture** principles with clear separation of concerns across four layers.

## Layer Structure

```
┌────────────────────────────────────────────────────────┐
│                    ROUTES LAYER                        │
│                      (app.py)                          │
│  • Route definitions (URL → Controller mapping)        │
│  • Flask app initialization                            │
│  • CORS configuration                                  │
│  • Error handlers (404, 500)                          │
└────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│                 CONTROLLER LAYER                       │
│              (car_fleet/controller.py)                 │
│  • RentalController class                              │
│  • HTTP request/response handling                      │
│  • Request validation                                  │
│  • JSON formatting                                     │
│  • HTTP status code determination                      │
└────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│                  SERVICE LAYER                         │
│               (car_fleet/service.py)                   │
│  • CarsRentalService class                             │
│  • Business logic                                      │
│  • Data transformation (Model → Dict)                  │
│  • Operation validation                                │
│  • Error handling (business errors)                    │
└────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│                   MODEL LAYER                          │
│         (car_fleet/car.py, agency.py)                  │
│  • Car class (data entity)                             │
│  • Agency class (data entity)                          │
│  • Domain entities                                     │
│  • Basic operations (is_available, etc.)               │
└────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Routes Layer (app.py)
**Purpose**: Define HTTP endpoints and delegate to controller

**Responsibilities**:
- Map URLs to controller methods
- Define HTTP methods (GET, POST, PUT, DELETE)
- Initialize application components
- Configure Flask middleware (CORS)
- Handle global errors

**Example**:
```python
@app.route("/api/cars/<registration>/rent", methods=["PUT"])
def rent_car(registration):
    return rental_controller.rent_car(registration)
```

**Key Principle**: Routes should be **thin** - just delegation, no logic.

---

### 2. Controller Layer (controller.py)
**Purpose**: Handle HTTP concerns and coordinate service calls

**Responsibilities**:
- Receive HTTP requests
- Extract and validate request data
- Call appropriate service methods
- Format responses as JSON
- Determine HTTP status codes
- Handle HTTP-specific errors

**Example**:
```python
def rent_car(self, registration: str) -> Tuple[Any, int]:
    success, car, error = self.rental_service.rent_car(registration)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"Car {car['brand']} rented successfully",
            "car": car
        }), 200
    
    status_code = 404 if "not found" in error.lower() else 400
    return jsonify({"success": False, "error": error}), status_code
```

**Key Principle**: Controllers should know about HTTP but not business rules.

---

### 3. Service Layer (service.py)
**Purpose**: Implement business logic and orchestrate model operations

**Responsibilities**:
- Execute business operations
- Validate business rules
- Coordinate multiple model operations
- Transform models to DTOs (dictionaries)
- Return success/failure tuples
- Handle business logic errors

**Example**:
```python
def rent_car(self, registration: str) -> tuple[bool, Optional[Dict], Optional[str]]:
    registration = registration.upper()
    
    # Find car
    car_dict = self.find_car_by_registration(registration)
    if not car_dict:
        return False, None, f"Car with registration {registration} not found"
    
    # Business rule: car must be available
    if not car_dict["availability"]:
        return False, None, f"Car {registration} is already rented"
    
    # Perform operation
    if self.agency.rent_car(registration):
        updated_car = self.find_car_by_registration(registration)
        return True, updated_car, None
    
    return False, None, "Failed to rent car"
```

**Key Principle**: Services should know about business rules but not HTTP.

---

### 4. Model Layer (car.py, agency.py)
**Purpose**: Represent domain entities and their basic operations

**Responsibilities**:
- Define data structures
- Basic entity operations
- Data validation (in constructors)
- Domain-specific methods

**Example**:
```python
class Car:
    def __init__(self, brand, model, year, registration):
        self.brand = brand
        self.model = model
        self.year = year
        self.registration = registration
        self.availability = True
    
    def is_available(self) -> bool:
        return self.availability
```

**Key Principle**: Models should be simple data containers with basic operations.

---

## Data Flow

### Request Flow (Client → Server)
```
1. HTTP Request
   ↓
2. Flask Route (app.py)
   @app.route("/api/cars/<reg>/rent", methods=["PUT"])
   ↓
3. Controller Method (controller.py)
   rental_controller.rent_car(registration)
   ↓
4. Service Method (service.py)
   rental_service.rent_car(registration)
   ↓
5. Model Operation (agency.py)
   agency.rent_car(registration)
   ↓
6. Model Update (car.py)
   car.availability = False
```

### Response Flow (Server → Client)
```
1. Model State (car.py)
   car.availability = False
   ↓
2. Service Response (service.py)
   return (True, car_dict, None)
   ↓
3. Controller Response (controller.py)
   return jsonify({"success": True, "car": car}), 200
   ↓
4. Flask Response (app.py)
   HTTP 200 with JSON body
   ↓
5. HTTP Response to Client
```

## Example: Adding a New Feature

Let's say we want to add a "reserve car" feature:

### 1. Update Model (car.py)
```python
class Car:
    def __init__(self, ...):
        ...
        self.reserved = False
```

### 2. Update Service (service.py)
```python
def reserve_car(self, registration: str) -> tuple[bool, Optional[Dict], Optional[str]]:
    car = self.find_car_by_registration(registration)
    if not car:
        return False, None, "Car not found"
    if not car["availability"]:
        return False, None, "Car not available"
    
    # Mark as reserved
    for c in self.agency.cars:
        if c.registration == registration:
            c.reserved = True
            return True, self.car_to_dict(c), None
```

### 3. Update Controller (controller.py)
```python
def reserve_car(self, registration: str) -> Tuple[Any, int]:
    success, car, error = self.rental_service.reserve_car(registration)
    if success:
        return jsonify({"success": True, "car": car}), 200
    return jsonify({"success": False, "error": error}), 400
```

### 4. Add Route (app.py)
```python
@app.route("/api/cars/<registration>/reserve", methods=["PUT"])
def reserve_car(registration):
    return rental_controller.reserve_car(registration)
```

Done! Each layer is updated independently with its specific concern.

## Benefits of This Architecture

### ✅ Separation of Concerns
Each layer has a single, well-defined responsibility.

### ✅ Testability
Each layer can be tested independently:
```python
# Test service without HTTP
service.rent_car("ABC-123")

# Test controller without Flask server
with app.app_context():
    controller.rent_car("ABC-123")
```

### ✅ Maintainability
Changes in one layer don't affect others:
- Change JSON format → only controller
- Change business rule → only service
- Change database → only models
- Add route → only app.py

### ✅ Reusability
Service layer can be used by:
- REST API (current)
- GraphQL API (future)
- CLI commands (future)
- Background jobs (future)
- WebSocket handlers (future)

### ✅ Scalability
Easy to extend:
- Add new endpoints → add route + controller method
- Add new business logic → add service method
- Add new entity → add model class

### ✅ Code Organization
Clear file structure:
```
car-fleet-api/
├── car_fleet/
│   ├── car.py         ← Models
│   ├── agency.py      ← Models
│   ├── service.py     ← Business Logic
│   └── controller.py  ← HTTP Logic
└── app.py            ← Routes
```

## Design Patterns Used

### 1. **MVC (Model-View-Controller)**
- **Model**: Car, Agency
- **View**: JSON responses
- **Controller**: RentalController

### 2. **Service Layer Pattern**
- Encapsulates business logic
- Coordinates model operations
- Independent of delivery mechanism

### 3. **Dependency Injection**
```python
agency = Agency()
service = CarsRentalService(agency)
controller = RentalController(service)
```

### 4. **Repository Pattern** (implicit)
- Agency acts as a repository for Cars
- Service abstracts data access

## Comparison: Monolithic vs Clean Architecture

### Monolithic (Before)
```python
@app.route("/api/cars/<registration>/rent")
def rent_car(registration):
    registration = registration.upper()
    for car in agency.cars:
        if car.registration == registration:
            if car.is_available():
                car.availability = False
                return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404
```
**Issues**: Mixed concerns, hard to test, not reusable

### Clean Architecture (After)
```python
# Route (app.py)
@app.route("/api/cars/<registration>/rent")
def rent_car(registration):
    return rental_controller.rent_car(registration)

# Controller (controller.py)
def rent_car(self, registration: str):
    success, car, error = self.rental_service.rent_car(registration)
    if success:
        return jsonify({"success": True, "car": car}), 200
    return jsonify({"error": error}), 404

# Service (service.py)
def rent_car(self, registration: str):
    car = self.find_car_by_registration(registration)
    if not car or not car["availability"]:
        return False, None, "Cannot rent"
    self.agency.rent_car(registration)
    return True, self.find_car_by_registration(registration), None
```
**Benefits**: Clear separation, testable, reusable

## File Organization

```
car-fleet-api/
├── car_fleet/                    # Package
│   ├── __init__.py              # Exports: Car, Agency, CarsRentalService, RentalController
│   ├── car.py                   # Model: Car entity
│   ├── agency.py                # Model: Agency entity
│   ├── service.py               # Service: Business logic
│   └── controller.py            # Controller: HTTP handling
│
├── app.py                        # Flask app: Route definitions
├── pyproject.toml               # UV configuration
├── uv.lock                      # Dependency lock
├── Dockerfile                   # Container definition
│
└── Documentation/
    ├── SERVICE_LAYER_REFACTORING.md
    ├── CONTROLLER_LAYER.md
    └── ARCHITECTURE_SUMMARY.md  # This file
```

## Summary

The Car Fleet API now implements **Clean Architecture** with:
- **4 distinct layers** with clear responsibilities
- **Separation of concerns** at every level
- **High testability** (each layer tested independently)
- **Easy maintenance** (change one layer without affecting others)
- **Scalability** (easy to add features or change implementations)

This architecture follows industry best practices and makes the codebase professional, maintainable, and extensible.
