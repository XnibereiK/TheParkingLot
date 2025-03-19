import unittest
from src.parking import ParkingLot, ParkingSpot, Vehicle  # Adjust if your module has a different name

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


class TestParkingSpot(unittest.TestCase):
    """Test cases for the ParkingSpot class."""

    def setUp(self):
        """Set up a parking spot and a vehicle before each test."""
        self.spot = ParkingSpot(1)
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
        self.assertIn("Spot 1 is already occupied", str(context.exception))

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
        self.assertIn("Spot 1 is already empty", str(context.exception))


class TestParkingLot(unittest.TestCase):
    """Test cases for the ParkingLot class."""

    def setUp(self):
        """Set up a parking lot with two spots before each test."""
        self.lot = ParkingLot()
        self.lot.add_spot(1)
        self.lot.add_spot(2)
        self.vehicle1 = Vehicle("CAR001", "Sedan", "Tesla", "Model 3", "White")
        self.vehicle2 = Vehicle("CAR002", "SUV", "Jeep", "Wrangler", "Black")

    def test_add_spot(self):
        """Test that adding spots increases the parking lot's size."""
        self.assertEqual(len(self.lot.parking_spots), 2)

    def test_park_vehicle_in_specific_spot(self):
        """Test parking a vehicle in a specific spot."""
        self.lot.park_vehicle(self.vehicle1, 1)
        self.assertFalse(self.lot.parking_spots[1].is_available)
        self.assertEqual(self.lot.parking_spots[1].vehicle, self.vehicle1)

    def test_park_vehicle_any_available_spot(self):
        """Test parking a vehicle in any available spot."""
        self.lot.park_vehicle(self.vehicle1)
        self.assertIn(self.vehicle1, [spot.vehicle for spot in self.lot.parking_spots.values()])

    def test_park_in_nonexistent_spot(self):
        """Test that parking in a nonexistent spot raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.lot.park_vehicle(self.vehicle1, 99)
        self.assertIn("Invalid spot ID: 99", str(context.exception))

    def test_park_in_occupied_spot(self):
        """Test that parking in an already occupied spot raises a ValueError."""
        self.lot.park_vehicle(self.vehicle1, 1)
        with self.assertRaises(ValueError) as context:
            self.lot.park_vehicle(self.vehicle2, 1)
        self.assertIn("Spot 1 is already occupied", str(context.exception))

    def test_park_when_no_spots_available(self):
        """Test that parking fails when there are no available spots."""
        self.lot.park_vehicle(self.vehicle1)
        self.lot.park_vehicle(self.vehicle2)
        with self.assertRaises(RuntimeError) as context:
            self.lot.park_vehicle(Vehicle("CAR003", "Truck", "Ford", "F-150", "Blue"))
        self.assertIn("No available spots left", str(context.exception))

    def test_unpark_vehicle(self):
        """Test successfully removing a parked vehicle."""
        self.lot.park_vehicle(self.vehicle1, 1)
        self.lot.unpark_vehicle(self.vehicle1.vehicle_id)
        self.assertTrue(self.lot.parking_spots[1].is_available)

    def test_unpark_nonexistent_vehicle(self):
        """Test that removing a nonexistent vehicle raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.lot.unpark_vehicle("NONEXIST")
        self.assertIn("Vehicle NONEXIST not found", str(context.exception))

    def test_release_spot(self):
        """Test releasing a parking spot."""
        self.lot.park_vehicle(self.vehicle1, 1)
        self.lot.release_spot(1)
        self.assertTrue(self.lot.parking_spots[1].is_available)

    def test_release_already_empty_spot(self):
        """Test that releasing an already empty spot raises a RuntimeError."""
        with self.assertRaises(RuntimeError) as context:
            self.lot.release_spot(1)
        self.assertIn("Spot 1 is already empty", str(context.exception))


if __name__ == "__main__":
    unittest.main()
