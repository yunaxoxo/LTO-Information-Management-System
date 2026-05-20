# Controller for driver-related operations
# Validates all inputs before delegating to the service layer
from models.driver_model import Driver
from services import driver_service
from db.query_helpers import (
    validate_not_empty,
    validate_in_set,
    validate_regex,
    validate_date_order,
    sanitize_string,
    to_date_string,
    LICENSE_NUMBER_REGEX,
    VALID_SEX,
    VALID_LICENSE_TYPES,
    VALID_LICENSE_STATUSES,
)


def _build_driver(data: dict) -> Driver:
    """
    Validates and constructs a Driver object from raw form data.
    Raises ValueError with a descriptive message on invalid input.
    """
    # Required string fields
    license_number = sanitize_string(data.get("license_number", ""), "License Number", min_len=1)
    validate_regex(license_number, LICENSE_NUMBER_REGEX, "License Number")

    full_name = sanitize_string(data.get("full_name", ""), "Full Name", min_len=2)
    address = sanitize_string(data.get("address", ""), "Address", min_len=2)

    # Enum fields
    sex = sanitize_string(data.get("sex", ""), "Sex")
    validate_in_set(sex, VALID_SEX, "Sex")

    license_type = sanitize_string(data.get("license_type", ""), "License Type")
    validate_in_set(license_type, VALID_LICENSE_TYPES, "License Type")

    license_status = sanitize_string(data.get("license_status", ""), "License Status")
    validate_in_set(license_status, VALID_LICENSE_STATUSES, "License Status")

    # Date fields
    birthday = to_date_string(data.get("birthday"), "Birthday")
    issuance = to_date_string(data.get("license_issuance_date"), "License Issuance Date")
    expiration = to_date_string(data.get("license_expiration_date"), "License Expiration Date")
    validate_date_order(issuance, expiration, "Issuance Date", "Expiration Date")

    # Dynamic status adjustment based on expiration date
    from datetime import date
    today_str = date.today().strftime("%Y-%m-%d")
    if license_status == "Expired" and expiration >= today_str:
        license_status = "Valid"
    elif license_status == "Valid" and expiration < today_str:
        license_status = "Expired"

    return Driver(
        license_number=license_number,
        full_name=full_name,
        birthday=birthday,
        sex=sex,
        address=address,
        license_type=license_type,
        license_status=license_status,
        license_issuance_date=issuance,
        license_expiration_date=expiration,
    )


# ============================================================
# CRUD Operations
# ============================================================

def create_driver(data: dict) -> str:
    """Validates input and creates a new driver."""
    driver = _build_driver(data)
    return driver_service.register_new_driver(driver)


def update_driver(data: dict) -> str:
    """Validates input and updates an existing driver. Primary key must be in data."""
    driver = _build_driver(data)
    return driver_service.update_driver_info(driver)


def delete_driver(license_number: str) -> str:
    """Validates the license number and deletes the driver."""
    license_number = sanitize_string(license_number, "License Number")
    validate_regex(license_number, LICENSE_NUMBER_REGEX, "License Number")
    return driver_service.delete_driver(license_number)


# ============================================================
# Read / Report Operations
# ============================================================

def get_drivers_by_criteria(filters: dict) -> list:
    """
    REPORT 1: Retrieves drivers matching the user-selected criteria.
    Accepts the frontend filter dict and maps keys to the service layer.
    """
    return driver_service.fetch_drivers_by_criteria(
        license_type=filters.get("license_type"),         # list from multiselect
        license_status=filters.get("license_status"),                     # list from multiselect
        sex=filters.get("sex", "ALL"),
        min_age=filters.get("min_age"),
        max_age=filters.get("max_age"),
    )


def get_invalid_licenses() -> list:
    """REPORT 4: Retrieves all drivers with expired or suspended licenses."""
    return driver_service.fetch_invalid_licenses()
