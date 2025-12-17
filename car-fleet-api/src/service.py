"""
Car Rental Service module
Service layer that abstracts business logic between Car and Agency
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agency import Agency
from .car import Car


class CarsRentalService:
    """Service layer for car rental operations."""

    def __init__(self, agency: Agency, data_file: str = "data/cars.json"):
        """
        Initialize the CarsRentalService.

        Args:
            agency (Agency): The agency instance to manage
            data_file (str): Path to the JSON data file
        """
        self.agency = agency
        self.data_file = Path(data_file)

    def load_from_json(self) -> tuple[bool, Optional[str]]:
        """
        Load cars from JSON file.

        Returns:
            tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            if not self.data_file.exists():
                return False, f"Data file {self.data_file} not found"

            with open(self.data_file, "r") as f:
                data = json.load(f)

            # Clear existing cars
            self.agency.cars.clear()

            # Load cars from JSON
            for car_data in data.get("cars", []):
                car = Car(
                    car_data["brand"],
                    car_data["model"],
                    car_data["year"],
                    car_data["registration"],
                )
                car.availability = car_data.get("availability", True)
                self.agency.cars.append(car)

            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            return False, f"Error loading data: {str(e)}"

    def save_to_json(self) -> tuple[bool, Optional[str]]:
        """
        Save cars to JSON file.

        Returns:
            tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            # Ensure directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert cars to dictionary format
            data = {"cars": [self.car_to_dict(car) for car in self.agency.cars]}

            # Write to file
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)

            return True, None
        except Exception as e:
            return False, f"Error saving data: {str(e)}"

    def get_agency_name(self) -> str:
        """Get the agency name."""
        return self.agency.name

    def car_to_dict(self, car: Car) -> Dict[str, Any]:
        """
        Convert a Car object to a dictionary.

        Args:
            car (Car): The car object to convert

        Returns:
            Dict[str, Any]: Dictionary representation of the car
        """
        return {
            "brand": car.brand,
            "model": car.model,
            "year": car.year,
            "registration": car.registration,
            "availability": car.availability,
        }

    def get_all_cars(self) -> List[Dict[str, Any]]:
        """
        Get all cars in the fleet.

        Returns:
            List[Dict[str, Any]]: List of all cars as dictionaries
        """
        return [self.car_to_dict(car) for car in self.agency.cars]

    def get_available_cars(self) -> List[Dict[str, Any]]:
        """
        Get all available cars in the fleet.

        Returns:
            List[Dict[str, Any]]: List of available cars as dictionaries
        """
        return [self.car_to_dict(car) for car in self.agency.cars if car.is_available()]

    def find_car_by_registration(self, registration: str) -> Optional[Dict[str, Any]]:
        """
        Find a car by its registration number.

        Args:
            registration (str): The registration number to search for

        Returns:
            Optional[Dict[str, Any]]: Car dictionary if found, None otherwise
        """
        registration = registration.upper()
        for car in self.agency.cars:
            if car.registration == registration:
                return self.car_to_dict(car)
        return None

    def add_car(
        self, brand: str, model: str, year: int, registration: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Add a new car to the fleet.

        Args:
            brand (str): Car brand
            model (str): Car model
            year (int): Manufacturing year
            registration (str): Registration number

        Returns:
            tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
                (success, car_dict, error_message)
        """
        registration = registration.upper()

        # Check if car already exists
        if self.find_car_by_registration(registration):
            return False, None, f"Car with registration {registration} already exists"

        # Create and add the car
        car = Car(brand, model, year, registration)
        if self.agency.add_car(car):
            self.save_to_json()  # Auto-save
            return True, self.car_to_dict(car), None

        return False, None, "Failed to add car"

    def rent_car(
        self, registration: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Rent a car by its registration number.

        Args:
            registration (str): The registration number of the car to rent

        Returns:
            tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
                (success, car_dict, error_message)
        """
        registration = registration.upper()

        # Check if car exists
        car_dict = self.find_car_by_registration(registration)
        if not car_dict:
            return False, None, f"Car with registration {registration} not found"

        # Check if car is available
        if not car_dict["availability"]:
            return False, None, f"Car {registration} is already rented"

        # Rent the car
        if self.agency.rent_car(registration):
            self.save_to_json()  # Auto-save
            updated_car = self.find_car_by_registration(registration)
            return True, updated_car, None

        return False, None, "Failed to rent car"

    def return_car(
        self, registration: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Return a rented car.

        Args:
            registration (str): The registration number of the car to return

        Returns:
            tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
                (success, car_dict, error_message)
        """
        registration = registration.upper()

        # Check if car exists
        car_dict = self.find_car_by_registration(registration)
        if not car_dict:
            return False, None, f"Car with registration {registration} not found"

        # Check if car is rented
        if car_dict["availability"]:
            return False, None, f"Car {registration} is already available"

        # Return the car
        if self.agency.return_car(registration):
            self.save_to_json()  # Auto-save
            updated_car = self.find_car_by_registration(registration)
            return True, updated_car, None

        return False, None, "Failed to return car"

    def delete_car(
        self, registration: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Delete a car from the fleet.

        Args:
            registration (str): The registration number of the car to delete

        Returns:
            tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
                (success, deleted_car_dict, error_message)
        """
        registration = registration.upper()

        # Find and delete the car
        for i, car in enumerate(self.agency.cars):
            if car.registration == registration:
                deleted_car = self.car_to_dict(car)
                del self.agency.cars[i]
                self.save_to_json()  # Auto-save
                return True, deleted_car, None

        return False, None, f"Car with registration {registration} not found"

    def get_fleet_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the fleet.

        Returns:
            Dict[str, Any]: Statistics including total, available, and rented cars
        """
        total_cars = len(self.agency.cars)
        available_cars = len([car for car in self.agency.cars if car.is_available()])
        rented_cars = total_cars - available_cars

        return {
            "total_cars": total_cars,
            "available_cars": available_cars,
            "rented_cars": rented_cars,
            "availability_rate": f"{(available_cars / total_cars * 100):.1f}%"
            if total_cars > 0
            else "0%",
        }
