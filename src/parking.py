"""Module for managing a parking lot system with vehicles and parking spots."""

from __future__ import annotations
import copy
import threading
from typing import Optional, Dict, Set, Callable, List, Any
from abc import ABC, abstractmethod


class ParkingLot:
    """Represents a parking lot with multiple parking spots."""
    parking_spots: Dict[int, BaseParkingSpot]
    vehicle_to_spot: Dict[str, int]  # Reverse lookup for fast search
    available_spots: Set[int]

    def __init__(self) -> None:
        """Initialize an empty parking lot and a reentrant lock."""
        self.parking_spots = {}
        self.vehicle_to_spot = {}
        self.available_spots = set()
        self._lock = threading.RLock()
        self._callbacks: Dict[str, List[Callable[..., None]]] = {}

    def __repr__(self) -> str:
        """Return a string representation of the parking lot's status."""
        with self._lock:
            if not self.parking_spots:
                return "uninitialized lot"
            lot_info = "\n".join(
                f"{spot_id}: {spot.vehicle.vehicle_type if spot.vehicle else 'empty'}"
                for spot_id, spot in self.parking_spots.items()
            )
            return f"-----------\n{lot_info}\n-----------"

    def register_callback(self, event: str, callback: Callable[..., None]) -> None:
        """
        Register a callback function for a specific event.
        
        Args:
            event (str): The event name (e.g., 'vehicle_parked', 'vehicle_unparked').
            callback (Callable[..., None]): The callback function to invoke.
        """
        with self._lock:
            if event not in self._callbacks:
                self._callbacks[event] = []
            self._callbacks[event].append(callback)

    def unregister_callback(self, event: str, callback: Callable[..., None]) -> None:
        """
        Unregister a callback function for a specific event.
        
        Args:
            event (str): The event name.
            callback (Callable[..., None]): The callback function to remove.
        """
        with self._lock:
            if event in self._callbacks and callback in self._callbacks[event]:
                self._callbacks[event].remove(callback)

    def _trigger_event(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Trigger all callbacks registered for the given event.
        
        Args:
            event (str): The event name.
            *args, **kwargs: Arguments to pass to the callbacks.
        """
        with self._lock:
            for callback in self._callbacks.get(event, []):
                callback(*args, **kwargs)

    def _find_available_spot(self) -> BaseParkingSpot:
        """
        Find the first available parking spot.
        
        Returns:
            BaseParkingSpot: A free parking spot.
        
        Raises:
            RuntimeError: If no available spots are left.
        """
        with self._lock:
            if not self.available_spots:
                raise RuntimeError("No available spots left.")
            spot_id = self.available_spots.pop()
            spot = self._get_spot_or_raise(spot_id)
            return spot

    def _get_spot_or_raise(self, spot_id: int) -> BaseParkingSpot:
        """
        Validate and retrieve a parking spot.
        
        Args:
            spot_id (int): The identifier of the parking spot.
        
        Returns:
            BaseParkingSpot: The parking spot object.
        
        Raises:
            ValueError: If the spot ID is invalid or does not exist.
        """
        with self._lock:
            if not isinstance(spot_id, int) or spot_id < 0:
                raise ValueError("Spot ID must be a non-negative integer.")
            if spot_id not in self.parking_spots:
                raise ValueError(f"Invalid spot ID: {spot_id}. The spot does not exist.")
            return self.parking_spots[spot_id]

    def add_spot(self, spot_id: int, spot_type: str = "standard") -> Optional[BaseParkingSpot]:
        """
        Add a parking spot to the lot.
        
        Args:
            spot_id (int): The unique identifier of the parking spot.
            spot_type (str): The type of parking spot ('standard' or 'electric').
        
        Returns:
            Optional[BaseParkingSpot]: The newly created parking spot or None if it already exists.
        
        Raises:
            ValueError: If the spot ID is invalid or the spot type is unknown.
        """
        with self._lock:
            if not isinstance(spot_id, int) or spot_id < 0:
                raise ValueError("Spot ID must be a non-negative integer.")
            if spot_id in self.parking_spots:
                return None  # Spot already exists
            if spot_type == "standard":
                spot = StandardParkingSpot(spot_id)
            elif spot_type == "electric":
                spot = ElectricVehicleParkingSpot(spot_id)
            else:
                raise ValueError(f"Unknown parking spot type: {spot_type}")
            self.parking_spots[spot_id] = spot
            self.available_spots.add(spot_id)
            return spot

    def take_snapshot(self) -> Dict[int, BaseParkingSpot]:
        """
        Take a deep copy snapshot of the current parking lot state.
        
        Returns:
            Dict[int, BaseParkingSpot]: A deep copy of the parking spots.
        """
        with self._lock:
            return copy.deepcopy(self.parking_spots)

    def park_vehicle(self, vehicle: Vehicle, spot_id: Optional[int] = None) -> None:
        """
        Park a vehicle in the lot.
        
        Args:
            vehicle (Vehicle): The vehicle to be parked.
            spot_id (Optional[int]): The specific spot to park in (if provided).
        
        Raises:
            TypeError: If the vehicle is not a Vehicle instance.
            RuntimeError: If the vehicle is already parked.
            ValueError: If the spot is occupied or does not exist.
        """
        with self._lock:
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
            self._trigger_event("vehicle_parked", vehicle=vehicle, spot=spot)

    def _free_spot(self, spot: BaseParkingSpot) -> None:
        """
        Free a parking spot and update available spots.
        
        Args:
            spot (BaseParkingSpot): The parking spot to be freed.
        
        Raises:
            RuntimeError: If the parking spot is already empty.
        """
        with self._lock:
            if spot.is_available:
                raise RuntimeError(f"Spot {spot.spot_id} is already empty.")
            spot.unpark_vehicle()
            self.available_spots.add(spot.spot_id)
            self._trigger_event("spot_freed", spot=spot)

    def unpark_vehicle(self, vehicle_id: str) -> None:
        """
        Unpark a vehicle from the parking lot.
        
        Args:
            vehicle_id (str): The unique identifier of the vehicle.
        
        Raises:
            ValueError: If the vehicle ID is invalid or the vehicle is not found.
        """
        with self._lock:
            if not isinstance(vehicle_id, str) or not vehicle_id.strip():
                raise ValueError("Invalid vehicle ID: must be a non-empty string.")
            if vehicle_id not in self.vehicle_to_spot:
                raise ValueError(f"Vehicle {vehicle_id} not found")
            spot_id = self.vehicle_to_spot.pop(vehicle_id)
            spot = self._get_spot_or_raise(spot_id)
            self._free_spot(spot)
            self._trigger_event("vehicle_unparked", vehicle_id=vehicle_id, spot=spot)

    def release_spot(self, spot_id: int) -> None:
        """
        Release a parking spot, making it available again.
        
        Args:
            spot_id (int): The ID of the spot to be released.
        
        Raises:
            ValueError: If the spot ID is invalid or does not exist.
            RuntimeError: If the parking spot is already empty.
        """
        with self._lock:
            spot = self._get_spot_or_raise(spot_id)
            self._free_spot(spot)


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
        """
        Initialize a vehicle.
        
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
        """
        Check if two vehicles are equal based on their ID.
        
        Args:
            other (object): The object to compare with.
        
        Returns:
            bool: True if the other object is a Vehicle with the same ID.
        """
        if not isinstance(other, Vehicle):
            raise TypeError("Only Vehicle instances can be compared.")
        return self.vehicle_id == other.vehicle_id


class BaseParkingSpot(ABC):
    """Abstract base class for a parking spot."""
    def __init__(self, spot_id: int) -> None:
        """
        Initialize a parking spot.
        
        Args:
            spot_id (int): Unique identifier for the spot.
        """
        self.spot_id = spot_id
        self.vehicle: Optional[Vehicle] = None

    def __repr__(self) -> str:
        """Return a string in the format 'PS# <spot_id>'."""
        return f"PS# {self.spot_id}"

    @property
    def is_available(self) -> bool:
        """Return True if no vehicle is parked."""
        return self.vehicle is None

    @abstractmethod
    def park_vehicle(self, vehicle: Vehicle) -> None:
        """
        Park a vehicle in the spot.
        Must be implemented by subclasses.
        """
        pass

    def unpark_vehicle(self) -> None:
        """
        Remove the parked vehicle.
        
        Raises:
            RuntimeError: If the spot is already empty.
        """
        if self.is_available:
            raise RuntimeError(f"Spot {self.spot_id} is already empty")
        self.vehicle = None


class StandardParkingSpot(BaseParkingSpot):
    """A standard parking spot for any vehicle."""
    def park_vehicle(self, vehicle: Vehicle) -> None:
        """
        Park a vehicle if the spot is free.
        
        Args:
            vehicle (Vehicle): The vehicle to park.
        
        Raises:
            TypeError: If the vehicle is not a Vehicle instance.
            ValueError: If the spot is occupied.
        """
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Expected a Vehicle instance.")
        if not self.is_available:
            raise ValueError(f"Spot {self.spot_id} is already occupied.")
        self.vehicle = vehicle


class ElectricVehicleParkingSpot(BaseParkingSpot):
    """A parking spot for electric vehicles with an optional charging port."""
    def __init__(self, spot_id: int, charging_port: bool = True) -> None:
        """
        Initialize an electric vehicle parking spot.
        
        Args:
            spot_id (int): Unique identifier.
            charging_port (bool, optional): Indicates presence of a charging port. Defaults to True.
        """
        super().__init__(spot_id)
        self.charging_port = charging_port

    def park_vehicle(self, vehicle: Vehicle) -> None:
        """
        Park an electric vehicle.
        
        Args:
            vehicle (Vehicle): The vehicle to park.
        
        Raises:
            TypeError: If not a Vehicle instance.
            ValueError: If the vehicle is not electric or the spot is occupied.
        """
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Expected a Vehicle instance.")
        if vehicle.vehicle_type != "electric":
            raise ValueError(f"Spot {self.spot_id} supports only electric vehicles.")
        if not self.is_available:
            raise ValueError(f"Spot {self.spot_id} is already occupied.")
        self.vehicle = vehicle
