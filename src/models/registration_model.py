# Data Structure for Registration Model
# Matches schema: vehicle_registrations table in seed.sql
class Registration:
    def __init__(
        self,
        registration_number,
        registration_date,
        expiration_date,
        registration_status,
        plate_number,
    ):
        self.registration_number = registration_number
        self.registration_date = registration_date
        self.expiration_date = expiration_date
        self.registration_status = registration_status
        self.plate_number = plate_number

    def __str__(self):
        return (
            f"Registration(Reg#: {self.registration_number}, "
            f"Plate: {self.plate_number}, Status: {self.registration_status})"
        )
