# Shared query-building utilities to enforce DRY across all services
import re
from datetime import date, datetime


def build_dynamic_where(filters: dict, column_map: dict):
    """
    Builds a dynamic WHERE clause from a dict of user-selected filter values.

    For each key in `column_map`, checks if `filters` contains a non-'ALL' value.
    If so, appends an `AND column = ?` clause and collects the parameter.

    Args:
        filters: dict of filter values from the UI, e.g. {"license_type": "Professional", "sex": "ALL"}
        column_map: dict mapping filter keys to SQL column names,
                     e.g. {"license_type": "license_type", "sex": "sex"}

    Returns:
        Tuple of (where_clause_string, params_tuple).
        The where_clause starts with "WHERE 1=1" so callers can always append.

    Example:
        clause, params = build_dynamic_where(
            {"license_type": "Professional", "sex": "ALL"},
            {"license_type": "license_type", "sex": "sex"}
        )
        # clause = "WHERE 1=1 AND license_type = ?"
        # params = ("Professional",)
    """
    conditions = []
    params = []

    for filter_key, column_name in column_map.items():
        value = filters.get(filter_key, "ALL")
        if (
            value is not None
            and str(value).strip().upper() != "ALL"
            and str(value).strip() != ""
        ):
            conditions.append(f"{column_name} = ?")
            params.append(value)

    where = "WHERE 1=1"
    if conditions:
        where += " AND " + " AND ".join(conditions)

    return where, tuple(params)


# ============================================================
# Input Validation Helpers
# ============================================================

LICENSE_NUMBER_REGEX = re.compile(r"^[A-Z]\d{2}-\d{2}-\d{6}$")
TOP_NUMBER_REGEX = re.compile(r"^[A-Z]-\d{6}-\d{7}$")
VALID_SEX = {"M", "F"}
VALID_LICENSE_TYPES = {"Student", "Non-Professional", "Professional"}
VALID_LICENSE_STATUSES = {"Valid", "Expired", "Suspended", "Revoked"}
VALID_REGISTRATION_STATUSES = {"Active", "Expired", "Suspended"}
VALID_VIOLATION_STATUSES = {"Unpaid", "Paid", "Contested"}


def validate_not_empty(value, field_name: str):
    """Raises ValueError if value is None or a blank string."""
    if value is None:
        raise ValueError(f"{field_name} is required and cannot be empty.")
    if isinstance(value, str) and value.strip() == "":
        raise ValueError(f"{field_name} is required and cannot be empty.")


def validate_in_set(value, allowed: set, field_name: str):
    """Raises ValueError if value is not in the allowed set."""
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}. Got: '{value}'")


def validate_regex(value: str, pattern: re.Pattern, field_name: str):
    """Raises ValueError if value doesn't match the regex pattern."""
    if not pattern.match(value):
        raise ValueError(
            f"{field_name} format is invalid: '{value}'. Expected pattern: {pattern.pattern}"
        )


def validate_positive_int(value, field_name: str):
    """Raises ValueError if value is not a non-negative integer."""
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer. Got: '{value}'")


def validate_year(value, field_name: str = "Year"):
    """Raises ValueError if year is not in [1900, 2027]."""
    if not isinstance(value, int) or not (1900 <= value <= 2027):
        raise ValueError(
            f"{field_name} must be an integer between 1900 and 2027. Got: '{value}'"
        )


def validate_date_order(start, end, start_name: str, end_name: str):
    """Raises ValueError if end date is not after start date."""
    if start > end:
        raise ValueError(f"{end_name} ({end}) must be after {start_name} ({start}).")


def sanitize_string(value: str, field_name: str, min_len: int = 1) -> str:
    """Strips whitespace and validates minimum length."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    cleaned = value.strip()
    if len(cleaned) < min_len:
        raise ValueError(
            f"{field_name} must be at least {min_len} characters after trimming. Got: '{cleaned}'"
        )
    return cleaned


def to_date_string(value, field_name: str) -> str:
    """
    Converts a date/datetime/string to a 'YYYY-MM-DD' string.
    Accepts datetime.date, datetime.datetime, or a string in 'YYYY-MM-DD' format.
    """
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        value = value.strip()
        # Validate format
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"{field_name} must be a valid date in YYYY-MM-DD format. Got: '{value}'"
            )
        return value
    raise ValueError(
        f"{field_name} must be a date or date-string. Got type: {type(value)}"
    )


def to_datetime_string(value, field_name: str) -> str:
    """
    Converts a datetime/string to 'YYYY-MM-DD HH:MM:SS' string.
    """
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, str):
        value = value.strip()
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(
                f"{field_name} must be in 'YYYY-MM-DD HH:MM:SS' format. Got: '{value}'"
            )
        return value
    raise ValueError(
        f"{field_name} must be a datetime or string. Got type: {type(value)}"
    )
