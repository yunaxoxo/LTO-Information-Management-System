# Data Structure for Vehicle Model
# Matches schema: vehicles table in seed.sql
class Vehicle:
    def __init__(
        self,
        plate_number,
        engine_number,
        chassis_number,
        make,
        model,
        year,
        color,
        vehicle_type,
        license_number,
    ):
        self.plate_number = plate_number
        self.engine_number = engine_number
        self.chassis_number = chassis_number
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.vehicle_type = vehicle_type
        self.license_number = license_number

    def __str__(self):
        return (
            f"Vehicle(Plate: {self.plate_number}, {self.year} {self.make} {self.model}, "
            f"Owner: {self.license_number})"
        )
