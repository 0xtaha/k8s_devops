#!/usr/bin/env python3
"""
Car Fleet Management API - Flask Backend
Orange DevOps Task - Python Programming Exercise
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from src import Agency, Car, CarsRentalService, RentalController

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Swagger UI configuration
SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI
API_URL = "/swagger.yaml"  # Our API specification file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Car Fleet Management API"},
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Initialize the agency, service, and controller
agency = Agency("Orange Car Rental")
rental_service = CarsRentalService(agency, data_file="data/cars.json")
rental_controller = RentalController(rental_service)

# Load cars from JSON file
success, error = rental_service.load_from_json()
if success:
    print(f"✓ Loaded {len(rental_service.get_all_cars())} cars from data/cars.json")
else:
    print(f"✗ Failed to load cars from JSON: {error}")
    print("Using empty fleet")


# Serve Swagger YAML file
@app.route("/swagger.yaml")
def swagger_spec():
    """Serve the Swagger specification file."""
    return send_from_directory(".", "swagger.yaml")


# Route definitions - delegating to controller
@app.route("/", methods=["GET"])
def home():
    """Home endpoint - API information."""
    return rental_controller.get_home()


@app.route("/api/cars", methods=["GET"])
def get_all_cars():
    """Get all cars in the fleet."""
    return rental_controller.get_all_cars()


@app.route("/api/cars/available", methods=["GET"])
def get_available_cars():
    """Get all available cars."""
    return rental_controller.get_available_cars()


@app.route("/api/cars/<registration>", methods=["GET"])
def get_car(registration):
    """Get details of a specific car."""
    return rental_controller.get_car(registration)


@app.route("/api/cars", methods=["POST"])
def add_car():
    """Add a new car to the fleet."""
    return rental_controller.add_car()


@app.route("/api/cars/<registration>/rent", methods=["PUT"])
def rent_car(registration):
    """Rent a car."""
    return rental_controller.rent_car(registration)


@app.route("/api/cars/<registration>/return", methods=["PUT"])
def return_car(registration):
    """Return a rented car."""
    return rental_controller.return_car(registration)


@app.route("/api/cars/<registration>", methods=["DELETE"])
def delete_car(registration):
    """Delete a car from the fleet."""
    return rental_controller.delete_car(registration)


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get fleet statistics."""
    return rental_controller.get_stats()


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚗 Car Fleet Management API Server")
    print("=" * 60)
    print(f"Agency: {rental_service.get_agency_name()}")
    print(f"Initial fleet size: {len(rental_service.get_all_cars())} cars")
    print("Server starting on http://127.0.0.1:5000")
    print(f"Swagger UI available at http://127.0.0.1:5000{SWAGGER_URL}")
    print("=" * 60 + "\n")

    app.run(debug=True, host="0.0.0.0", port=5000)
