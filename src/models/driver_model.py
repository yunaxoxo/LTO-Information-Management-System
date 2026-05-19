# Data Structure for Driver Model
# Matches schema: drivers table in seed.sql
class Driver:
    def __init__(
        self,
        license_number,
        full_name,
        birthday,
        sex,
        address,
        license_type,
        license_status,
        license_issuance_date,
        license_expiration_date,
    ):
        self.license_number = license_number
        self.full_name = full_name
        self.birthday = birthday
        self.sex = sex
        self.address = address
        self.license_type = license_type
        self.license_status = license_status
        self.license_issuance_date = license_issuance_date
        self.license_expiration_date = license_expiration_date

    def __str__(self):
        return (
            f"Driver(License: {self.license_number}, Name: {self.full_name}, "
            f"Type: {self.license_type}, Status: {self.license_status})"
        )
