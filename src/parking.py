"""Module for managing a parking lot system with vehicles and parking spots."""

from __future__ import annotations
import copy
from typing import Optional, Dict, Set


class ParkingLot:
    """Represents a parking lot with multiple parking spots."""
    parking_spots: Dict[int, ParkingSpot]
    vehicle_to_spot: Dict[str, int]
    available_spots: Set[int]

    def __init__(self) -> None:
        """Initialize an empty parking lot."""
        self.parking_spots = {}
        self.vehicle_to_spot = {}  # Reverse lookup for fast search
        self.available_spots = set()

    def __repr__(self) -> str:
        """Return a string representation of the parking lot's status."""
        if not self.parking_spots:
            return "uninitialized lot"

        lot_info = "\n".join(
            f"{spot_id}: {spot.vehicle.vehicle_type if spot.vehicle else 'empty'}"
            for spot_id, spot in self.parking_spots.items()
        )
        return f"-----------\n{lot_info}\n-----------"

    def _find_available_spot(self) -> ParkingSpot:
        """Find the first available parking spot.

        Returns:
            ParkingSpot: A free parking spot.

        Raises:
            RuntimeError: If no available spots are left.
        """
        if not self.available_spots:
            raise RuntimeError("No available spots left.")

        spot_id = self.available_spots.pop()
        spot = self._get_spot_or_raise(spot_id)
        return spot

    def _get_spot_or_raise(self, spot_id: int) -> ParkingSpot:
        """Validate and retrieve a parking spot.

        Args:
            spot_id (int): The identifier of the parking spot.

        Returns:
            ParkingSpot: The parking spot object.

        Raises:
            ValueError: If the spot ID is invalid or does not exist.
        """
        if not isinstance(spot_id, int) or spot_id < 0:
            raise ValueError("Spot ID must be a non-negative integer.")
        if spot_id not in self.parking_spots:
            raise ValueError(f"Invalid spot ID: {spot_id}. The spot does not exist.")
        return self.parking_spots[spot_id]

    def add_spot(self, spot_id: int) -> Optional[ParkingSpot]:
        """Add a parking spot to the lot.

        Args:
            spot_id (int): The unique identifier of the parking spot.

        Returns:
            Optional[ParkingSpot]: The newly created parking spot or None if it already exists.

        Raises:
            ValueError: If the spot ID is not a valid integer.
        """
        if not isinstance(spot_id, int) or spot_id < 0:
            raise ValueError("Spot ID must be a non-negative integer.")

        if spot_id in self.parking_spots:
            return None  # Spot already exists

        spot = ParkingSpot(spot_id)
        self.parking_spots[spot_id] = spot
        self.available_spots.add(spot_id)
        return spot

    def take_snapshot(self) -> Dict[int, ParkingSpot]:
        """Take a deep copy snapshot of the current parking lot state.

        Returns:
            Dict[int, ParkingSpot]: A deep copy of the parking spots.
        """
        return copy.deepcopy(self.parking_spots)

    def park_vehicle(self, vehicle: Vehicle, spot_id: Optional[int] = None) -> None:
        """Park a vehicle in the lot.

        Args:
            vehicle (Vehicle): The vehicle to be parked.
            spot_id (Optional[int]): The specific spot to park in (if provided).

        Raises:
            TypeError: If the vehicle is not an instance of Vehicle.
            RuntimeError: If the vehicle is already parked.
            ValueError: If the spot is occupied or does not exist.
        """
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Expected a Vehicle instance.")

        if vehicle.vehicle_id in self.vehicle_to_spot:
            raise RuntimeError("Vehicle already parked.")

        if spot_id is None:
            spot = self._find_available_spot()
        else:
            spot = self._get_spot_or_raise(spot_id)
            if not spot.is_available:
                raise ValueError(f"Spot {spot.spot_id} is already occupied.")

        spot.park_vehicle(vehicle)
        self.vehicle_to_spot[vehicle.vehicle_id] = spot.spot_id
        self.available_spots.discard(spot.spot_id)

    def _free_spot(self, spot: ParkingSpot) -> None:
        """Helper to free a parking spot and update available spots.

        Args:
            spot (ParkingSpot): The parking spot to be freed.

        Raises:
            RuntimeError: If the parking spot is already empty.
        """
        if spot.is_available:
            raise RuntimeError(f"Spot {spot.spot_id} is already empty.")
        spot.unpark_vehicle()
        self.available_spots.add(spot.spot_id)

    def unpark_vehicle(self, vehicle_id: str) -> None:
        """Unpark a vehicle from the parking lot.

        Args:
            vehicle_id (str): The unique identifier of the vehicle.

        Raises:
            ValueError: If the vehicle ID is invalid or the vehicle is not found.
        """
        if not isinstance(vehicle_id, str) or not vehicle_id.strip():
            raise ValueError("Invalid vehicle ID: must be a non-empty string.")
        if vehicle_id not in self.vehicle_to_spot:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        spot_id = self.vehicle_to_spot.pop(vehicle_id)
        spot = self._get_spot_or_raise(spot_id)
        self._free_spot(spot)

    def release_spot(self, spot_id: int) -> None:
        """Release a parking spot, making it available again.

        Args:
            spot_id (int): The ID of the spot to be released.

        Raises:
            ValueError: If the spot ID is invalid or does not exist.
            RuntimeError: If the parking spot is already empty.
        """
        spot = self._get_spot_or_raise(spot_id)
        self._free_spot(spot)


class ParkingSpot:
    """Represents an individual parking spot."""

    def __init__(self, spot_id: int) -> None:
        """Initialize a parking spot.

        Args:
            spot_id (int): The unique identifier of the parking spot.
        """
        self.vehicle: Optional[Vehicle] = None
        self.spot_id = spot_id

    def __repr__(self) -> str:
        """Return a string representation of the parking spot."""
        return f"PS# {self.spot_id}"

    @property
    def is_available(self) -> bool:
        """Check if the parking spot is available.

        Returns:
            bool: True if the spot is available, False otherwise.
        """
        return self.vehicle is None

    def park_vehicle(self, vehicle: Vehicle) -> None:
        """Park a vehicle in the parking spot.

        Args:
            vehicle (Vehicle): The vehicle to be parked.

        Raises:
            TypeError: If the argument is not an instance of Vehicle.
            ValueError: If the parking spot is already occupied.
        """
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Expected a Vehicle instance.")

        if not self.is_available:
            raise ValueError(f"Spot {self.spot_id} is already occupied.")

        self.vehicle = vehicle

    def unpark_vehicle(self) -> None:
        """Remove the vehicle from the parking spot.

        Raises:
            RuntimeError: If the parking spot is already empty.
        """
        if self.is_available:
            raise RuntimeError(f"Spot {self.spot_id} is already empty.")

        self.vehicle = None


class Vehicle:
    """Represents a vehicle that can be parked in the parking lot."""

    def __init__(
        self,
        vehicle_id: str,
        vehicle_type: str,
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        vehicle_color: Optional[str] = None
    ) -> None:
        """Initialize a vehicle.

        Args:
            vehicle_id (str): The unique identifier of the vehicle.
            vehicle_type (str): The type of the vehicle (e.g., car, truck).
            vehicle_make (Optional[str]): The make of the vehicle.
            vehicle_model (Optional[str]): The model of the vehicle.
            vehicle_color (Optional[str]): The color of the vehicle.

        Raises:
            ValueError: If vehicle_id or vehicle_type are empty or invalid.
        """
        if not isinstance(vehicle_id, str) or not vehicle_id.strip():
            raise ValueError("Vehicle ID must be a non-empty string.")

        if not isinstance(vehicle_type, str) or not vehicle_type.strip():
            raise ValueError("Vehicle type must be a non-empty string.")

        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.vehicle_make = vehicle_make
        self.vehicle_model = vehicle_model
        self.vehicle_color = vehicle_color

    def __repr__(self) -> str:
        """Return a string representation of the vehicle."""
        return f"Vehicle(id={self.vehicle_id}, type={self.vehicle_type})"

    def __eq__(self, other: object) -> bool:
        """Check if two vehicles are equal based on their ID.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the other object is a Vehicle with the same ID.
        """
        if not isinstance(other, Vehicle):
            raise TypeError("Only Vehicle instances can be compared.")
        return self.vehicle_id == other.vehicle_id
