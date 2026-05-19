from db.db_connection import execute_query

def get_total_drivers() -> int:
    query = "SELECT COUNT(*) AS val FROM drivers"
    res = execute_query(query, ())
    return res[0]['val'] if res else 0

def get_active_registrations() -> int:
    query = "SELECT COUNT(*) AS val FROM vehicle_registrations WHERE registration_status = 'Active'"
    res = execute_query(query, ())
    return res[0]['val'] if res else 0

def get_total_revenue() -> int:
    # Uses Paid violations as revenue 
    query = "SELECT COALESCE(SUM(fine_amount), 0) AS val FROM traffic_violations WHERE violation_status = 'Paid'"
    res = execute_query(query, ())
    return int(res[0]['val']) if res else 0

def get_pending_violations() -> int:
    query = "SELECT COUNT(*) AS val FROM traffic_violations WHERE violation_status = 'Unpaid'"
    res = execute_query(query, ())
    return res[0]['val'] if res else 0

def get_expiring_licenses() -> int:
    # Licenses expiring within the next 30 days
    query = """
        SELECT COUNT(*) AS val 
        FROM drivers 
        WHERE license_expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    """
    res = execute_query(query, ())
    return res[0]['val'] if res else 0

def get_resolved_violations() -> int:
    query = "SELECT COUNT(*) AS val FROM traffic_violations WHERE violation_status = 'Paid'"
    res = execute_query(query, ())
    return res[0]['val'] if res else 0

def get_average_fine() -> float:
    query = "SELECT COALESCE(AVG(fine_amount), 0) AS val FROM traffic_violations"
    res = execute_query(query, ())
    return float(res[0]['val']) if res else 0

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