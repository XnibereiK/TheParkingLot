import unittest
from src.parking import (
    ParkingLot,
    StandardParkingSpot,                
    ElectricVehicleParkingSpot,
    Vehicle
)

class TestVehicle(unittest.TestCase):
    """Test cases for the Vehicle class."""

    def test_vehicle_creation(self):
        """Test vehicle initialization and attribute assignments."""
        vehicle = Vehicle("ABC123", "Sedan", "Toyota", "Corolla", "Blue")
        self.assertEqual(vehicle.vehicle_id, "ABC123")
        self.assertEqual(vehicle.vehicle_type, "Sedan")
        self.assertEqual(vehicle.vehicle_make, "Toyota")
        self.assertEqual(vehicle.vehicle_model, "Corolla")
        self.assertEqual(vehicle.vehicle_color, "Blue")


class TestStandardParkingSpot(unittest.TestCase):
    """Test cases for the StandardParkingSpot (aliased as ParkingSpot) class."""

    def setUp(self):
        """Set up a standard parking spot and a vehicle before each test."""
        self.spot = StandardParkingSpot(1)
        self.vehicle = Vehicle("XYZ789", "SUV", "Honda", "CRV", "Red")

    def test_initially_available(self):
        """Test that a new parking spot is available."""
        self.assertTrue(self.spot.is_available)

    def test_park_vehicle(self):
        """Test parking a vehicle in an available spot."""
        self.spot.park_vehicle(self.vehicle)
        self.assertFalse(self.spot.is_available)
        self.assertEqual(self.spot.vehicle, self.vehicle)

    def test_park_vehicle_in_occupied_spot(self):
        """Test that parking in an occupied spot raises a ValueError."""
        self.spot.park_vehicle(self.vehicle)
        with self.assertRaises(ValueError) as context:
            self.spot.park_vehicle(Vehicle("NEW123", "Truck", "Ford", "F-150", "Black"))
        self.assertIn("already occupied", str(context.exception))

    def test_unpark_vehicle(self):
        """Test removing a parked vehicle."""
        self.spot.park_vehicle(self.vehicle)
        self.spot.unpark_vehicle()
        self.assertTrue(self.spot.is_available)
        self.assertIsNone(self.spot.vehicle)

    def test_unpark_empty_spot(self):
        """Test that trying to unpark an empty spot raises RuntimeError."""
        with self.assertRaises(RuntimeError) as context:
            self.spot.unpark_vehicle()
        self.assertIn("already empty", str(context.exception))


class TestElectricVehicleParkingSpot(unittest.TestCase):
    """Test cases for the ElectricVehicleParkingSpot class."""

    def setUp(self):
        """Set up an electric parking spot and sample vehicles before each test."""
        self.electric_spot = ElectricVehicleParkingSpot(10)
        # Create an electric vehicle and a non-electric vehicle.
        self.electric_vehicle = Vehicle("ELECTRO1", "electric", "Tesla", "Model S", "Red")
        self.non_electric_vehicle = Vehicle("NONEL1", "Sedan", "Toyota", "Camry", "Blue")

    def test_electric_vehicle_parking(self):
        """Test that an electric vehicle can be parked in an electric spot."""
        self.electric_spot.park_vehicle(self.electric_vehicle)
        self.assertFalse(self.electric_spot.is_available)
        self.assertEqual(self.electric_spot.vehicle, self.electric_vehicle)

    def test_reject_non_electric_vehicle(self):
        """Test that parking a non-electric vehicle in an electric spot raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.electric_spot.park_vehicle(self.non_electric_vehicle)
        self.assertIn("supports only electric vehicles", str(context.exception))

    def test_unpark_vehicle(self):
        """Test removing a parked electric vehicle."""
        self.electric_spot.park_vehicle(self.electric_vehicle)
        self.electric_spot.unpark_vehicle()
        self.assertTrue(self.electric_spot.is_available)
        self.assertIsNone(self.electric_spot.vehicle)


class TestParkingLot(unittest.TestCase):
    """Test cases for the ParkingLot class."""

    def setUp(self):
        """Set up a parking lot with a standard and an electric spot before each test."""
        self.lot = ParkingLot()
        self.lot.add_spot(1)                      # Standard spot (default)
        self.lot.add_spot(2, spot_type="electric")  # Electric spot
        self.vehicle1 = Vehicle("CAR001", "Sedan", "Tesla", "Model 3", "White")
        self.vehicle2 = Vehicle("CAR002", "SUV", "Jeep", "Wrangler", "Black")
        self.electric_vehicle = Vehicle("ELECTRO1", "electric", "Nissan", "Leaf", "Green")

    def test_add_spot(self):
        """Test that adding spots increases the parking lot's size."""
        self.assertEqual(len(self.lot.parking_spots), 2)

    def test_park_vehicle_in_specific_standard_spot(self):
        """Test parking a vehicle in a specific standard spot."""
        self.lot.park_vehicle(self.vehicle1, 1)
        self.assertFalse(self.lot.parking_spots[1].is_available)
        self.assertEqual(self.lot.parking_spots[1].vehicle, self.vehicle1)

    def test_park_vehicle_in_specific_electric_spot_with_incorrect_vehicle(self):
        """Test that parking a non-electric vehicle in an electric spot raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.lot.park_vehicle(self.vehicle1, 2)  # vehicle1 is not electric
        self.assertIn("supports only electric vehicles", str(context.exception))

    def test_park_electric_vehicle_in_electric_spot(self):
        """Test that an electric vehicle can be parked in an electric spot."""
        self.lot.park_vehicle(self.electric_vehicle, 2)
        self.assertFalse(self.lot.parking_spots[2].is_available)
        self.assertEqual(self.lot.parking_spots[2].vehicle, self.electric_vehicle)

    def test_park_vehicle_any_available_spot(self):
        """Test parking a vehicle in any available spot."""
        self.lot.park_vehicle(self.vehicle1)
        parked_spots = [spot for spot in self.lot.parking_spots.values() if spot.vehicle is not None]
        self.assertIn(self.vehicle1, [spot.vehicle for spot in parked_spots])

    def test_park_in_nonexistent_spot(self):
        """Test that parking in a nonexistent spot raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.lot.park_vehicle(self.vehicle1, 99)
        self.assertIn("Invalid spot ID: 99", str(context.exception))

    def test_park_in_occupied_spot(self):
        """Test that parking in an already occupied spot raises ValueError."""
        self.lot.park_vehicle(self.vehicle1, 1)
        with self.assertRaises(ValueError) as context:
            self.lot.park_vehicle(self.vehicle2, 1)
        self.assertIn("already occupied", str(context.exception))

    def test_park_when_no_spots_available(self):
        """Test that parking fails when there are no available spots."""
        self.lot.park_vehicle(self.vehicle1)
        self.lot.park_vehicle(self.electric_vehicle, 2)
        with self.assertRaises(RuntimeError) as context:
            self.lot.park_vehicle(Vehicle("CAR003", "Truck", "Ford", "F-150", "Blue"))
        self.assertIn("No available spots left", str(context.exception))

    def test_unpark_vehicle(self):
        """Test successfully removing a parked vehicle."""
        self.lot.park_vehicle(self.vehicle1, 1)
        self.lot.unpark_vehicle(self.vehicle1.vehicle_id)
        self.assertTrue(self.lot.parking_spots[1].is_available)

    def test_unpark_nonexistent_vehicle(self):
        """Test that removing a nonexistent vehicle raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.lot.unpark_vehicle("NONEXIST")
        self.assertIn("Vehicle NONEXIST not found", str(context.exception))

    def test_release_spot(self):
        """Test releasing a parking spot."""
        self.lot.park_vehicle(self.vehicle1, 1)
        self.lot.release_spot(1)
        self.assertTrue(self.lot.parking_spots[1].is_available)

    def test_release_already_empty_spot(self):
        """Test that releasing an already empty spot raises RuntimeError."""
        with self.assertRaises(RuntimeError) as context:
            self.lot.release_spot(1)
        self.assertIn("already empty", str(context.exception))


if __name__ == "__main__":
    unittest.main()
