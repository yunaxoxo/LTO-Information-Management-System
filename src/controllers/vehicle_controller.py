# Controller for vehicle-related operations
# Validates all inputs before delegating to the service layer
from models.vehicle_model import Vehicle
from services import vehicle_service
from db.query_helpers import (
    validate_not_empty,
    validate_regex,
    validate_year,
    sanitize_string,
    to_date_string,
    LICENSE_NUMBER_REGEX,
)


def _build_vehicle(data: dict) -> Vehicle:
    """
    Validates and constructs a Vehicle object from raw form data.
    Raises ValueError with a descriptive message on invalid input.
    """
    plate_number = sanitize_string(data.get("plate_number", ""), "Plate Number", min_len=5)
    if len(plate_number) > 7:
        raise ValueError(f"Plate Number must be 5-7 characters. Got {len(plate_number)}.")

    engine_number = sanitize_string(data.get("engine_number", ""), "Engine Number")
    chassis_number = sanitize_string(data.get("chassis_number", ""), "Chassis Number")
    make = sanitize_string(data.get("make", ""), "Make")
    model = sanitize_string(data.get("model", ""), "Model")
    color = sanitize_string(data.get("color", ""), "Color")
    vehicle_type = sanitize_string(data.get("vehicle_type", ""), "Vehicle Type")

    # Year must be an integer
    year_raw = data.get("year")
    validate_not_empty(year_raw, "Year")
    year = int(year_raw)
    validate_year(year)

    # Owner license number
    license_number = sanitize_string(data.get("license_number", ""), "License Number")
    validate_regex(license_number, LICENSE_NUMBER_REGEX, "Owner License Number")

    return Vehicle(
        plate_number=plate_number,
        engine_number=engine_number,
        chassis_number=chassis_number,
        make=make,
        model=model,
        year=year,
        color=color,
        vehicle_type=vehicle_type,
        license_number=license_number,
    )


# ============================================================
# CRUD Operations
# ============================================================

def create_vehicle(data: dict) -> str:
    """Validates input and creates a new vehicle."""
    vehicle = _build_vehicle(data)
    return vehicle_service.register_new_vehicle(vehicle)


def update_vehicle(data: dict) -> str:
    """Validates input and updates an existing vehicle."""
    vehicle = _build_vehicle(data)
    return vehicle_service.update_vehicle_info(vehicle)


def delete_vehicle(plate_number: str) -> str:
    """Validates the plate number and deletes the vehicle."""
    plate_number = sanitize_string(plate_number, "Plate Number", min_len=5)
    return vehicle_service.delete_vehicle(plate_number)


# ============================================================
# Read / Report Operations
# ============================================================

def get_vehicles_by_criteria(filters: dict) -> list:
    """Retrieves vehicles matching user-selected filter criteria."""
    return vehicle_service.fetch_vehicles_by_criteria(
        make=filters.get("make", "ALL"),
        model=filters.get("model", "ALL"),
        year=filters.get("year", "ALL"),
        color=filters.get("color", "ALL"),
        vehicle_type=filters.get("vehicle_type", "ALL"),
        license_number=filters.get("license_number", "ALL"),
    )


def get_vehicles_by_owner(license_number: str) -> list:
    """REPORT 2: Retrieves all vehicles owned by a given driver."""
    license_number = sanitize_string(license_number, "License Number")
    validate_regex(license_number, LICENSE_NUMBER_REGEX, "License Number")
    return vehicle_service.fetch_vehicles_by_owner(license_number)


def get_expired_registrations(as_of_date) -> list:
    """REPORT 3: Retrieves vehicles with expired registrations as of a given date."""
    date_str = to_date_string(as_of_date, "As-Of Date")
    return vehicle_service.fetch_expired_registrations(date_str)
