-- REPORT 1 -> View all registered drivers filtered by: License type, License status, Age range, Sex
SELECT *
FROM drivers
WHERE
    (? = 'ALL' OR license_type = ?)
AND (? = 'ALL' OR license_status = ?)
AND (? = 'ALL' OR sex = ?)
AND (
    TIMESTAMPDIFF(YEAR, birthday, CURDATE())
    BETWEEN ? AND ?
);

-- REPORT 2 -> View all vehicles owned by a given driver.
SELECT *
FROM vehicles
WHERE license_number = ?;

-- REPORT 3 -> View all vehicles with expired registrations as of a given date.
SELECT v.*
FROM vehicles v
JOIN vehicle_registrations r
    ON v.plate_number = r.plate_number
WHERE r.expiration_date < ?;

-- REPORT 4 -> View all drivers with expired or suspended licenses.
SELECT *
FROM drivers
WHERE license_status IN ('Expired', 'Suspended');

-- REPORT 5 -> View all traffic violations committed by a given driver within a specified date range.
SELECT *
FROM traffic_violations
WHERE license_number = ?
AND violation_date BETWEEN ? AND ?;

--REPORT 6 -> View the total number of violations per violation type for a given year.
SELECT
    violation_type,
    COUNT(*) AS total_violations
FROM traffic_violations
WHERE violation_date BETWEEN ? AND ?
GROUP BY violation_type;

-- REPORT 7 -> View all vehicles involved in violations within a given city or region.
SELECT *
FROM traffic_violations
WHERE location LIKE CONCAT('%', ?, '%');
