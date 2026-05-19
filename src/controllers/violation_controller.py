# Controller for traffic violation operations
# Validates all inputs before delegating to the service layer
from db.query_helpers import (
    LICENSE_NUMBER_REGEX,
    TOP_NUMBER_REGEX,
    VALID_VIOLATION_STATUSES,
    sanitize_string,
    to_date_string,
    to_datetime_string,
    validate_in_set,
    validate_not_empty,
    validate_positive_int,
    validate_regex,
)
from models.violation_model import Violation
from services import violation_service


def _build_violation(data: dict) -> Violation:
    """
    Validates and constructs a Violation object from raw form data.
    Raises ValueError with a descriptive message on invalid input.
    """
    top_number = sanitize_string(data.get("top_number", ""), "TOP Number")
    validate_regex(top_number, TOP_NUMBER_REGEX, "TOP Number")

    violation_type = sanitize_string(data.get("violation_type", ""), "Violation Type")
    location = sanitize_string(data.get("location", ""), "Location")
    officer = sanitize_string(
        data.get("apprehending_officer", ""), "Apprehending Officer"
    )

    violation_status = sanitize_string(
        data.get("violation_status", ""), "Violation Status"
    )
    validate_in_set(violation_status, VALID_VIOLATION_STATUSES, "Violation Status")

    # Fine amount must be a non-negative integer
    fine_raw = data.get("fine_amount")
    validate_not_empty(fine_raw, "Fine Amount")
    fine_amount = int(fine_raw)
    validate_positive_int(fine_amount, "Fine Amount")

    # Violation date (DATETIME)
    violation_date = to_datetime_string(data.get("violation_date"), "Violation Date")

    # License number (required FK)
    license_number = sanitize_string(data.get("license_number", ""), "License Number")
    validate_regex(license_number, LICENSE_NUMBER_REGEX, "License Number")

    # Plate number (optional — NULL for pedestrian violations)
    plate_raw = data.get("plate_number")
    plate_number = None
    if plate_raw is not None and str(plate_raw).strip() != "":
        plate_number = sanitize_string(str(plate_raw), "Plate Number", min_len=5)

    return Violation(
        top_number=top_number,
        violation_type=violation_type,
        violation_date=violation_date,
        location=location,
        apprehending_officer=officer,
        violation_status=violation_status,
        fine_amount=fine_amount,
        license_number=license_number,
        plate_number=plate_number,
    )


# ============================================================
# CRUD Operations
# ============================================================


def create_violation(data: dict) -> str:
    """Validates input and records a new traffic violation."""
    violation = _build_violation(data)
    return violation_service.record_new_traffic_violation(violation)


def update_violation(data: dict) -> str:
    """Validates input and updates an existing traffic violation."""
    violation = _build_violation(data)
    return violation_service.update_traffic_violation(violation)


def delete_violation(top_number: str) -> str:
    """Validates the TOP number and deletes the violation."""
    top_number = sanitize_string(top_number, "TOP Number")
    validate_regex(top_number, TOP_NUMBER_REGEX, "TOP Number")
    return violation_service.delete_traffic_violation(top_number)


# ============================================================
# Read / Report Operations
# ============================================================


def get_violations_by_criteria(filters: dict) -> list:
    """Retrieves violations matching user-selected filter criteria."""
    return violation_service.fetch_traffic_violations_by_criteria(
        violation_type=filters.get("violation_type", "ALL"),
        violation_status=filters.get("violation_status", "ALL"),
        license_number=filters.get("license_number", "ALL"),
        plate_number=filters.get("plate_number", "ALL"),
    )


def get_violations_by_driver(license_number: str, start_date, end_date) -> list:
    """
    REPORT 5: Retrieves violations for a specific driver within a date range.
    """
    license_number = sanitize_string(license_number, "License Number")
    validate_regex(license_number, LICENSE_NUMBER_REGEX, "License Number")
    start = to_date_string(start_date, "Start Date")
    end = to_date_string(end_date, "End Date")
    return violation_service.fetch_violations_by_driver(license_number, start, end)


def get_violation_counts_by_type(start_date, end_date) -> list:
    """
    REPORT 6: Retrieves violation counts grouped by type for a date range.
    """
    start = to_date_string(start_date, "Start Date")
    end = to_date_string(end_date, "End Date")
    return violation_service.fetch_violation_counts_by_type(start, end)


def get_violations_by_location(location: str) -> list:
    """
    REPORT 7: Retrieves violations matching a city/region name (partial match).
    """
    location = sanitize_string(location, "Location", min_len=2)
    return violation_service.fetch_violations_by_location(location)
