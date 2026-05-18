-- REPORT 1
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

-- REPORT 2
SELECT *
FROM vehicles
WHERE license_number = ?;

-- REPORT 3
SELECT v.*
FROM vehicles v
JOIN vehicle_registrations r
    ON v.plate_number = r.plate_number
WHERE r.expiration_date < ?;

-- REPORT 4
SELECT *
FROM drivers
WHERE license_status IN ('Expired', 'Suspended');

-- REPORT 5
SELECT *
FROM traffic_violations
WHERE license_number = ?
AND violation_date BETWEEN ? AND ?;

--REPORT 6
SELECT
    violation_type,
    COUNT(*) AS total_violations
FROM traffic_violations
WHERE violation_date BETWEEN ? AND ?
GROUP BY violation_type;

-- REPORT 7
SELECT *
FROM traffic_violations
WHERE location LIKE CONCAT('%', ?, '%');
