# Data Structure for Violation Model
# Matches schema: traffic_violations table in seed.sql
# NOTE: violation_id is AUTO_INCREMENT — not included here; it's assigned by the DB.
class Violation:
    def __init__(
        self,
        top_number,
        violation_type,
        violation_date,
        location,
        apprehending_officer,
        violation_status,
        fine_amount,
        license_number,
        plate_number=None,
    ):
        self.top_number = top_number
        self.violation_type = violation_type
        self.violation_date = violation_date
        self.location = location
        self.apprehending_officer = apprehending_officer
        self.violation_status = violation_status
        self.fine_amount = fine_amount
        self.license_number = license_number
        self.plate_number = plate_number  # Nullable — pedestrian violations have no plate

    def __str__(self):
        return (
            f"Violation(TOP: {self.top_number}, Type: {self.violation_type}, "
            f"Status: {self.violation_status}, Fine: {self.fine_amount})"
        )
