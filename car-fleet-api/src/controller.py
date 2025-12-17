"""
Rental Controller module
Controller layer that handles HTTP requests and responses for car rental operations
"""

from typing import Any, Tuple

from flask import jsonify, request

from .service import CarsRentalService


class RentalController:
    """Controller for handling car rental HTTP requests."""

    def __init__(self, rental_service: CarsRentalService):
        """
        Initialize the RentalController.

        Args:
            rental_service (CarsRentalService): The service instance to use
        """
        self.rental_service = rental_service

    def get_home(self) -> Tuple[Any, int]:
        """
        Home endpoint - API information.

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        return jsonify(
            {
                "message": "Car Fleet Management API",
                "version": "1.0",
                "agency": self.rental_service.get_agency_name(),
                "endpoints": {
                    "GET /": "API information",
                    "GET /api/cars": "Get all cars",
                    "GET /api/cars/available": "Get available cars",
                    "GET /api/cars/<registration>": "Get car details",
                    "POST /api/cars": "Add a new car",
                    "PUT /api/cars/<registration>/rent": "Rent a car",
                    "PUT /api/cars/<registration>/return": "Return a car",
                    "DELETE /api/cars/<registration>": "Delete a car",
                    "GET /api/stats": "Get fleet statistics",
                },
            }
        ), 200

    def get_all_cars(self) -> Tuple[Any, int]:
        """
        Get all cars in the fleet.

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        cars = self.rental_service.get_all_cars()
        return jsonify({"success": True, "count": len(cars), "cars": cars}), 200

    def get_available_cars(self) -> Tuple[Any, int]:
        """
        Get all available cars.

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        available_cars = self.rental_service.get_available_cars()
        return jsonify(
            {"success": True, "count": len(available_cars), "cars": available_cars}
        ), 200

    def get_car(self, registration: str) -> Tuple[Any, int]:
        """
        Get details of a specific car.

        Args:
            registration (str): The car registration number

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        car = self.rental_service.find_car_by_registration(registration)

        if car:
            return jsonify({"success": True, "car": car}), 200

        return jsonify(
            {
                "success": False,
                "error": f"Car with registration {registration.upper()} not found",
            }
        ), 404

    def add_car(self) -> Tuple[Any, int]:
        """
        Add a new car to the fleet.

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        data = request.get_json()

        # Validate required fields
        required_fields = ["brand", "model", "year", "registration"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify(
                {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}",
                }
            ), 400

        try:
            year = int(data["year"])
            success, car, error = self.rental_service.add_car(
                data["brand"], data["model"], year, data["registration"]
            )

            if success:
                return jsonify(
                    {
                        "success": True,
                        "message": f"Car {car['brand']} {car['model']} ({car['registration']}) added successfully",
                        "car": car,
                    }
                ), 201
            else:
                return jsonify({"success": False, "error": error}), 400

        except ValueError:
            return jsonify(
                {"success": False, "error": f"Invalid year value: {data.get('year')}"}
            ), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    def rent_car(self, registration: str) -> Tuple[Any, int]:
        """
        Rent a car.

        Args:
            registration (str): The car registration number

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        success, car, error = self.rental_service.rent_car(registration)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": f"Car {car['brand']} {car['model']} ({car['registration']}) rented successfully",
                    "car": car,
                }
            ), 200

        # Determine status code based on error
        status_code = 404 if "not found" in error.lower() else 400
        return jsonify({"success": False, "error": error}), status_code

    def return_car(self, registration: str) -> Tuple[Any, int]:
        """
        Return a rented car.

        Args:
            registration (str): The car registration number

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        success, car, error = self.rental_service.return_car(registration)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": f"Car {car['brand']} {car['model']} ({car['registration']}) returned successfully",
                    "car": car,
                }
            ), 200

        # Determine status code based on error
        status_code = 404 if "not found" in error.lower() else 400
        return jsonify({"success": False, "error": error}), status_code

    def delete_car(self, registration: str) -> Tuple[Any, int]:
        """
        Delete a car from the fleet.

        Args:
            registration (str): The car registration number

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        success, car, error = self.rental_service.delete_car(registration)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": f"Car {car['registration']} deleted successfully",
                    "car": car,
                }
            ), 200

        return jsonify({"success": False, "error": error}), 404

    def get_stats(self) -> Tuple[Any, int]:
        """
        Get fleet statistics.

        Returns:
            Tuple[Any, int]: JSON response and status code
        """
        stats = self.rental_service.get_fleet_stats()
        return jsonify({"success": True, "stats": stats}), 200
