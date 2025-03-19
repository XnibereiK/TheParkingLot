import sys
import os

# Append the src directory to the system path
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

from parking import ParkingLot, ParkingSpot, Vehicle

if __name__ == "__main__":
    lot = ParkingLot()
    print(lot)