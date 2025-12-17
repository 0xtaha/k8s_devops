"""
Car class module
Represents a car in the rental fleet
"""


class Car:
    """Represents a car in the rental fleet."""

    def __init__(self, brand, model, year, registration):
        """
        Initialize a Car object.

        Args:
            brand (str): The car's brand
            model (str): The car's model
            year (int): The car's manufacturing year
            registration (str): The car's registration number
        """
        self.brand = brand
        self.model = model
        self.year = year
        self.registration = registration
        self.availability = True

    def display_details(self):
        """Display the car's information."""
        status = "Available" if self.availability else "Rented"
        print(f"\n{'=' * 50}")
        print(f"Registration: {self.registration}")
        print(f"Brand: {self.brand}")
        print(f"Model: {self.model}")
        print(f"Year: {self.year}")
        print(f"Status: {status}")
        print(f"{'=' * 50}")

    def is_available(self):
        """
        Check if the car is available for rent.

        Returns:
            bool: True if available, False otherwise
        """
        return self.availability
