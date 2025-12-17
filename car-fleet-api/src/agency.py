"""
Agency class module
Represents a car rental agency managing a fleet of cars
"""


class Agency:
    """Represents a car rental agency managing a fleet of cars."""

    def __init__(self, name="Orange Car Rental"):
        """
        Initialize an Agency object.

        Args:
            name (str): The name of the agency
        """
        self.name = name
        self.cars = []

    def add_car(self, car):
        """
        Add a car to the fleet.

        Args:
            car (Car): The car object to add

        Returns:
            bool: True if successful, False otherwise
        """
        # Check if registration already exists
        for existing_car in self.cars:
            if existing_car.registration == car.registration:
                print(
                    f"\nError: Car with registration {car.registration} already exists!"
                )
                return False

        self.cars.append(car)
        print(f"\nCar {car.brand} {car.model} ({car.registration}) added successfully!")
        return True

    def rent_car(self, registration):
        """
        Mark a car as rented.

        Args:
            registration (str): The registration number of the car to rent

        Returns:
            bool: True if successful, False otherwise
        """
        for car in self.cars:
            if car.registration == registration:
                if car.is_available():
                    car.availability = False
                    print(
                        f"\nCar {car.brand} {car.model} ({registration}) rented successfully!"
                    )
                    return True
                else:
                    print(f"\nError: Car {registration} is already rented!")
                    return False

        print(f"\nError: Car with registration {registration} not found!")
        return False

    def return_car(self, registration):
        """
        Make a car available after return.

        Args:
            registration (str): The registration number of the car to return

        Returns:
            bool: True if successful, False otherwise
        """
        for car in self.cars:
            if car.registration == registration:
                if not car.is_available():
                    car.availability = True
                    print(
                        f"\nCar {car.brand} {car.model} ({registration}) returned successfully!"
                    )
                    return True
                else:
                    print(f"\nError: Car {registration} is already available!")
                    return False

        print(f"\nError: Car with registration {registration} not found!")
        return False

    def display_available_cars(self):
        """Display all cars that are available for rent."""
        available_cars = [car for car in self.cars if car.is_available()]

        if not available_cars:
            print("\nNo cars available for rent.")
            return

        print(f"\n{'=' * 50}")
        print(f"Available Cars at {self.name}")
        print(f"{'=' * 50}")

        for car in available_cars:
            print(f"{car.registration} - {car.brand} {car.model} ({car.year})")

        print(f"{'=' * 50}")
        print(f"Total available: {len(available_cars)}")

    def display_all_cars(self):
        """Display all cars in the fleet with their status."""
        if not self.cars:
            print("\nNo cars in the fleet.")
            return

        print(f"\n{'=' * 50}")
        print(f"All Cars at {self.name}")
        print(f"{'=' * 50}")

        for car in self.cars:
            status = "Available" if car.is_available() else "Rented"
            print(
                f"{car.registration} - {car.brand} {car.model} ({car.year}) - [{status}]"
            )

        print(f"{'=' * 50}")
        print(f"Total cars: {len(self.cars)}")
