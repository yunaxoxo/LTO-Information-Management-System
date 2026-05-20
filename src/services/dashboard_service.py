from db.db_connection import execute_query


def get_total_drivers() -> int:
    query = "SELECT COUNT(*) AS val FROM drivers"
    res = execute_query(query, ())
    return res[0]["val"] if res else 0


def get_active_registrations() -> int:
    query = "SELECT COUNT(*) AS val FROM vehicle_registrations WHERE registration_status = 'Active'"
    res = execute_query(query, ())
    return res[0]["val"] if res else 0


def get_total_revenue() -> int:
    # Uses Paid violations as revenue
    query = "SELECT COALESCE(SUM(fine_amount), 0) AS val FROM traffic_violations WHERE violation_status = 'Paid'"
    res = execute_query(query, ())
    return int(res[0]["val"]) if res else 0


def get_pending_violations() -> int:
    query = "SELECT COUNT(*) AS val FROM traffic_violations WHERE violation_status = 'Unpaid'"
    res = execute_query(query, ())
    return res[0]["val"] if res else 0


def get_expiring_licenses() -> int:
    # Licenses expiring within the next 30 days
    query = """
        SELECT COUNT(*) AS val 
        FROM drivers 
        WHERE license_expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    """
    res = execute_query(query, ())
    return res[0]["val"] if res else 0


def get_resolved_violations() -> int:
    query = (
        "SELECT COUNT(*) AS val FROM traffic_violations WHERE violation_status = 'Paid'"
    )
    res = execute_query(query, ())
    return res[0]["val"] if res else 0


def get_average_fine() -> float:
    query = "SELECT COALESCE(AVG(fine_amount), 0) AS val FROM traffic_violations"
    res = execute_query(query, ())
    return float(res[0]["val"]) if res else 0


def get_monthly_registration_trend() -> list:
    # Groups registrations by month for the current year
    query = """
        SELECT DATE_FORMAT(registration_date, '%b') AS month, COUNT(*) AS count 
        FROM vehicle_registrations 
        WHERE YEAR(registration_date) = YEAR(CURDATE()) 
        GROUP BY MONTH(registration_date), month 
        ORDER BY MONTH(registration_date)
    """
    return execute_query(query, ())

def get_total_drivers_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM drivers", ())
    return res[0]['val'] if res else 0

def get_valid_licenses_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM drivers WHERE license_status = 'Valid'", ())
    return res[0]['val'] if res else 0

def get_expired_licenses_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM drivers WHERE license_status = 'Expired'", ())
    return res[0]['val'] if res else 0

def get_suspended_licenses_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM drivers WHERE license_status IN ('Suspended','Revoked')", ())
    return res[0]['val'] if res else 0

def get_total_vehicles_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM vehicles", ())
    return res[0]['val'] if res else 0

def get_most_common_vehicle_type() -> str:
    res = execute_query(
        "SELECT vehicle_type, COUNT(*) AS cnt FROM vehicles GROUP BY vehicle_type ORDER BY cnt DESC LIMIT 1", ()
    )
    return res[0]['vehicle_type'] if res else "N/A"

def get_total_registrations_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM vehicle_registrations", ())
    return res[0]['val'] if res else 0

def get_expired_registrations_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM vehicle_registrations WHERE registration_status = 'Expired'", ())
    return res[0]['val'] if res else 0

def get_expiring_registrations_count() -> int:
    res = execute_query(
        """SELECT COUNT(*) AS val FROM vehicle_registrations
           WHERE registration_status = 'Active'
           AND expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)""", ()
    )
    return res[0]['val'] if res else 0

def get_total_violations_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM traffic_violations", ())
    return res[0]['val'] if res else 0

def get_contested_violations_count() -> int:
    res = execute_query("SELECT COUNT(*) AS val FROM traffic_violations WHERE violation_status = 'Contested'", ())
    return res[0]['val'] if res else 0

def get_total_fines_collected() -> float:
    res = execute_query("SELECT COALESCE(SUM(fine_amount),0) AS val FROM traffic_violations WHERE violation_status='Paid'", ())
    return float(res[0]['val']) if res else 0.0
