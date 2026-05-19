"""Driver entity — SQL and data access only (no Streamlit)."""

import database as db

_AGE_EXPR = "TIMESTAMPDIFF(YEAR, birthday, CURDATE())"


def get_all_drivers(license_type=None, license_status=None, age_min=None, age_max=None, sex=None):
    conditions = []
    params = []
    if license_type and license_type != "All Types":
        conditions.append("license_type = %s")
        params.append(license_type)
    if statuses:
        placeholders = ", ".join(["%s"] * len(statuses))
        conditions.append(f"license_status IN ({placeholders})")
        params.extend(statuses)
    if age_min is not None:
        conditions.append(f"{_AGE_EXPR} >= %s")
        params.append(age_min)
    if age_max is not None:
        conditions.append(f"{_AGE_EXPR} <= %s")
        params.append(age_max)
    if sex and sex != "All":
        sex_val = "M" if sex == "Male" else "F" if sex == "Female" else sex[0]
        conditions.append("sex = %s")
        params.append(sex_val)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"""
        SELECT full_name, license_number, license_type, license_status,
               birthday, sex, address, license_issuance_date, license_expiration_date,
               {_AGE_EXPR} AS age
        FROM drivers {where}
        ORDER BY full_name
    """
    return db.execute_query(query, params)


def get_driver_by_license(license_number):
    rows = db.execute_query(
        f"""
        SELECT license_number, full_name, birthday, sex, address, license_type,
               license_status, license_issuance_date, license_expiration_date,
               {_AGE_EXPR} AS age
        FROM drivers WHERE license_number = %s
        """,
        (license_number.strip(),),
    )
    return rows[0] if rows else None


def add_driver(data):
    query = """
        INSERT INTO drivers (
            license_number, full_name, birthday, sex, address,
            license_type, license_status, license_issuance_date, license_expiration_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data["license_number"],
        data["full_name"],
        data["birthday"],
        data["sex"],
        data["address"],
        data["license_type"],
        data["license_status"],
        data["license_issuance_date"],
        data["license_expiration_date"],
    )
    db.execute_query(query, params, fetch=False)


def update_driver(license_number, data):
    query = """
        UPDATE drivers SET full_name=%s, birthday=%s, sex=%s, address=%s,
            license_type=%s, license_status=%s,
            license_issuance_date=%s, license_expiration_date=%s
        WHERE license_number=%s
    """
    params = (
        data["full_name"],
        data["birthday"],
        data["sex"],
        data["address"],
        data["license_type"],
        data["license_status"],
        data["license_issuance_date"],
        data["license_expiration_date"],
        license_number,
    )
    db.execute_query(query, params, fetch=False)


def delete_driver(license_number):
    db.execute_query(
        "DELETE FROM drivers WHERE license_number = %s",
        (license_number,),
        fetch=False,
    )


def get_drivers_expired_or_suspended():
    return db.execute_query("""
        SELECT full_name, license_number, license_type, license_status,
               license_expiration_date, address
        FROM drivers
        WHERE license_status IN ('Expired', 'Suspended')
        ORDER BY full_name
    """)

