CREATE DATABASE IF NOT EXISTS `lto_system`;
USE `lto_system`;

-- Disable key checks temporarily to avoid deployment order lockouts
SET FOREIGN_KEY_CHECKS = 0;

-- ========================================================
-- DROP EXISTING TABLES IN REVERSE CONSTRAINT ORDER
-- ========================================================
DROP TABLE IF EXISTS `traffic_violations`;
DROP TABLE IF EXISTS `vehicle_registrations`;
DROP TABLE IF EXISTS `vehicles`;
DROP TABLE IF EXISTS `drivers`;

SET FOREIGN_KEY_CHECKS = 1;

-- ========================================================
-- CREATE AND POPULATE: DRIVER TABLE
-- ========================================================
CREATE TABLE drivers (
    license_number VARCHAR(15) PRIMARY KEY NOT NULL CHECK (license_number REGEXP '^[A-Z][0-9]{2}-[0-9]{2}-[0-9]{6}$'),
    full_name VARCHAR(100) NOT NULL CHECK (LENGTH(TRIM(full_name)) >= 2), 
    birthday DATE NOT NULL,
    sex VARCHAR(1) NOT NULL CHECK (sex IN ('M', 'F')), 
    address VARCHAR(100) NOT NULL, 
    license_type ENUM('Student', 'Non-Professional', 'Professional') NOT NULL,
    license_status ENUM('Valid', 'Expired', 'Suspended', 'Revoked') NOT NULL DEFAULT 'Valid', 
    license_issuance_date DATE NOT NULL,
    license_expiration_date DATE NOT NULL,
    CONSTRAINT chk_license_lifetime CHECK (license_expiration_date > license_issuance_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO drivers (license_number, full_name, birthday, sex, address, age, license_type, license_status, license_issuance_date, license_expiration_date) VALUES
-- Scenario A: Fleet Owners & Transport Operators (1-10)
('A01-15-100001', 'Juan Jose Santos', '1980-04-12', 'M', 'Quezon City, Metro Manila','Professional', 'Valid', '2021-04-12', '2031-04-12'),
('B02-18-100002', 'Maria Clarissa Cruz', '1985-08-22', 'F', 'Pasig City, Metro Manila', 'Professional', 'Valid', '2023-08-22', '2033-08-22'),
('C03-12-100003', 'Antonio Luna Reyes', '1974-11-05', 'M', 'Caloocan City, Metro Manila', 'Professional', 'Valid', '2022-11-05', '2032-11-05'),
('D04-19-100004', 'Grace Poe Llamanzares', '1982-01-30', 'F', 'Makati City, Metro Manila', 'Professional', 'Valid', '2024-01-30', '2034-01-30'),
('E05-20-100005', 'Edgardo Jose San Diego', '1978-06-15', 'M', 'Mandaluyong City, Metro Manila', 'Professional', 'Valid', '2025-06-15', '2035-06-15'),
('F06-14-100006', 'Corazon Aquino Ramos', '1988-09-18', 'F', 'Taguig City, Metro Manila', 'Professional', 'Valid', '2021-09-18', '2031-09-18'),
('G07-11-100007', 'Fernando Poe Rosario', '1969-03-25', 'M', 'Manila, Metro Manila', 'Professional', 'Valid', '2022-03-25', '2032-03-25'),
('H08-16-100008', 'Imelda Marcos Romualdez', '1976-07-02', 'F', 'San Juan, Metro Manila', 'Non-Professional', 'Valid', '2023-07-02', '2033-07-02'),
('I09-17-100009', 'Benigno Simeon Aquino', '1983-12-11', 'M', 'Las Pinas, Metro Manila',  'Professional', 'Valid', '2024-12-11', '2034-12-11'),
('J10-13-100010', 'Gloria Macapagal Arroyo', '1971-05-04', 'F', 'Pampanga',  'Professional', 'Valid', '2021-05-04', '2031-05-04'),

-- Scenario B: Expired Profiles / Suspended System Records (11-20)
('K11-22-100011', 'Rodrigo Roa Duterte', '1945-03-28', 'M', 'Davao City',  'Non-Professional', 'Expired', '2016-03-28', '2021-03-28'),
('L12-21-100012', 'Joseph Ejercito Estrada', '1937-04-19', 'M', 'San Juan, Metro Manila',  'Professional', 'Suspended', '2021-04-19', '2026-04-19'),
('M13-23-100013', 'Fidel Valdez Ramos', '1958-03-18', 'M', 'Pangasinan', 'Professional', 'Revoked', '2023-03-18', '2033-03-18'),
('N14-15-100014', 'Miriam Defensor Santiago', '1965-06-15', 'F', 'Iloilo City', 'Non-Professional', 'Expired', '2015-06-15', '2020-06-15'),
('O15-19-100015', 'Manuel Roxas Araneta', '1970-05-13', 'M', 'Capiz', 'Professional', 'Suspended', '2024-05-13', '2029-05-13'),
('P16-18-100016', 'Alan Peter Cayetano', '1975-10-28', 'M', 'Taguig, Metro Manila', 'Non-Professional', 'Expired', '2018-10-28', '2023-10-28'),
('Q17-20-100017', 'Francis Pancratius Pangilinan', '1963-08-24', 'M', 'Quezon City', 'Non-Professional', 'Revoked', '2020-08-24', '2025-08-24'),
('R18-12-100018', 'Loren Legarda Bautista', '1960-01-28', 'F', 'Malabon', 'Non-Professional', 'Expired', '2012-01-28', '2022-01-28'),
('S19-14-100019', 'Panfilo Morena Lacson', '1948-06-01', 'M', 'Subic', 'Professional', 'Suspended', '2022-06-01', '2027-06-01'),
('T20-11-100020', 'Gregorio Ballesteros Honasan', '1948-03-14', 'M', 'Bicol', 'Non-Professional', 'Expired', '2011-03-14', '2021-03-14'),

-- Scenario C: Habitual Traffic Violators (21-35)
('U21-16-100021', 'Michael Vincent Castro', '1992-02-14', 'M', 'Manila, Metro Manila', 'Non-Professional', 'Valid', '2021-02-14', '2031-02-14'),
('V22-17-100022', 'Ronaldo Del Rosario', '1989-11-30', 'M', 'Paranaque, Metro Manila', 'Professional', 'Valid', '2022-11-30', '2032-11-30'),
('W23-18-100023', 'Jessica Mae Mendoza', '1995-07-19', 'F', 'Pasay City, Metro Manila', 'Non-Professional', 'Valid', '2023-07-19', '2033-07-19'),
('X24-19-100024', 'Mark Anthony Santos', '1991-04-05', 'M', 'Valenzuela, Metro Manila', 'Non-Professional', 'Valid', '2024-04-05', '2034-04-05'),
('Y25-20-100025', 'Divine Grace Pascual', '1993-09-22', 'F', 'Muntinlupa, Metro Manila', 'Non-Professional', 'Valid', '2020-09-22', '2030-09-22'),
('Z26-15-100026', 'Christian Paul Reyes', '1987-12-25', 'M', 'Marikina, Metro Manila', 'Professional', 'Valid', '2025-12-25', '2035-12-25'),
('A27-14-100027', 'Stephanie Nicole Villanueva', '1996-05-14', 'F', 'Navotas, Metro Manila', 'Non-Professional', 'Valid', '2021-05-14', '2031-05-14'),
('B28-13-100028', 'Jonathan David Aquino', '1984-03-03', 'M', 'Malabon, Metro Manila', 'Professional', 'Valid', '2022-03-03', '2032-03-03'),
('C29-12-100029', 'Patricia Marie Cruz', '1998-10-10', 'F', 'Pateros, Metro Manila', 'Student', 'Valid', '2025-10-10', '2026-10-10'),
('D30-11-100030', 'Christopher John Pineda', '1990-08-12', 'M', 'Taguig, Metro Manila', 'Non-Professional', 'Valid', '2023-08-12', '2033-08-12'),
('E31-19-100031', 'Mary Grace Soriano', '1994-01-01', 'F', 'San Jose Del Monte, Bulacan', 'Non-Professional', 'Valid', '2024-01-01', '2034-01-01'),
('F32-18-100032', 'Jose Mari Chan', '1955-09-04', 'M', 'Iloilo', 'Non-Professional', 'Valid', '2021-09-04', '2031-09-04'),
('G33-17-100033', 'Arnel Pineda Campaner', '1967-09-05', 'M', 'Olongapo', 'Non-Professional', 'Valid', '2022-09-05', '2032-09-05'),
('H34-16-100034', 'Manuel Luis Quezon', '1990-08-19', 'M', 'Baler, Aurora', 'Non-Professional', 'Valid', '2023-08-19', '2033-08-19'),
('I35-15-100035', 'Sergio Osmena Suico', '1988-09-09', 'M', 'Cebu City', 'Professional', 'Valid', '2024-09-09', '2034-09-09'),

-- Scenario D: Standard Clean Benchmarks (36-50)
('J36-21-100036', 'Leandro Loco Villon', '2000-01-15', 'M', 'Mataas Na Kahoy, Batangas', 'Non-Professional', 'Valid', '2021-01-15', '2031-01-15'),
('K37-22-100037', 'Camila Cabello Dimaculangan', '2001-03-20', 'F', 'Lipa City, Batangas', 'Non-Professional', 'Valid', '2022-03-20', '2032-03-20'),
('L38-23-100038', 'Arthur Nery Hernandez', '1999-05-14', 'M', 'Tanauan, Batangas', 'Non-Professional', 'Valid', '2023-05-14', '2033-05-14'),
('M39-24-100039', 'Moira Dela Torre Santos', '1993-11-04', 'F', 'Davao City', 'Non-Professional', 'Valid', '2024-11-04', '2034-11-04'),
('N40-25-100040', 'Sarah Geronimo Guidicelli', '1988-07-25', 'F', 'Pampanga', 'Non-Professional', 'Valid', '2025-07-25', '2035-07-25'),
('O41-11-100041', 'Regine Velasquez Alcasid', '1970-04-22', 'F', 'Bulacan', 'Non-Professional', 'Valid', '2021-04-22', '2031-04-22'),
('P42-12-100042', 'Ogie Herminio Alcasid', '1967-08-27', 'M', 'Manila', 'Non-Professional', 'Valid', '2022-08-27', '2032-08-27'),
('Q43-13-100043', 'Gary Valenciano Valenciano', '1964-08-06', 'M', 'Camarines Sur', 'Non-Professional', 'Valid', '2023-08-06', '2033-08-06'),
('R44-14-100044', 'Martin Ramon Nievera', '1962-02-05', 'M', 'Manila', 'Non-Professional', 'Valid', '2024-02-05', '2034-02-05'),
('S45-15-100045', 'Kylie Fausto Padilla', '1993-01-25', 'F', 'Laguna', 'Non-Professional', 'Valid', '2025-01-25', '2035-01-25'),
('T46-16-100046', 'Daniel John Padilla', '1995-04-26', 'M', 'Tacloban', 'Non-Professional', 'Valid', '2021-04-26', '2031-04-26'),
('U47-17-100047', 'Kathryn Bernardo Manuel', '1996-03-26', 'F', 'Cabanatuan', 'Non-Professional', 'Valid', '2022-03-26', '2032-03-26'),
('V48-18-100048', 'Enrique Gil Baccon', '1992-03-30', 'M', 'Cebu', 'Non-Professional', 'Valid', '2023-03-30', '2033-03-30'),
('W49-19-100049', 'Liza Hope Soberano', '1998-01-04', 'F', 'Pangasinan', 'Non-Professional', 'Valid', '2024-01-04', '2034-01-04'),
('X50-20-100050', 'James Reid Bonifacio', '1993-05-11', 'M', 'Makati', 'Non-Professional', 'Valid', '2025-05-11', '2035-05-11');

-- ========================================================
-- CREATE AND POPULATE: VEHICLE TABLE
-- ========================================================
-- Note: 15 drivers are purposefully omitted here so they do not own vehicles.
CREATE TABLE vehicles (
  plate_number VARCHAR(7) PRIMARY KEY NOT NULL CHECK (LENGTH(TRIM(plate_number)) BETWEEN 5 AND 7),
  engine_number VARCHAR(17) NOT NULL, 
  chassis_number VARCHAR(17) NOT NULL, 
  make VARCHAR(30) NOT NULL,
  model VARCHAR(30) NOT NULL CHECK (LENGTH(TRIM(model)) >= 1),
  year INT NOT NULL CHECK (year BETWEEN 1900 AND 2027), 
  color VARCHAR(30) NOT NULL, 
  vehicle_type VARCHAR(30) NOT NULL,
  license_number VARCHAR(15) NOT NULL,
  CONSTRAINT uk_vehicle_engine_number UNIQUE(engine_number),
  CONSTRAINT uk_vehicle_chassis_number UNIQUE(chassis_number),
  CONSTRAINT fk_vehicle_license_number
      FOREIGN KEY (license_number) REFERENCES drivers (license_number)
      ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO vehicles (plate_number, engine_number, chassis_number, make, model, year, color, vehicle_type, license_number) VALUES
('ABC1234', 'ENG-998122X', 'CHA-441029384-A', 'Toyota', 'Vios', 2019, 'Silver', 'Sedan', 'A01-15-100001'),
('XYZ7890', 'ENG-112039A', 'CHA-882019283-B', 'Mitsubishi', 'Mirage G4', 2021, 'Red', 'Sedan', 'B02-18-100002'),
('NEB4561', 'ENG-554631D', 'CHA-991028374-C', 'Honda', 'Civic', 2018, 'Modern Steel', 'Sedan', 'C03-12-100003'),
('NCP8822', 'ENG-773612K', 'CHA-112093847-D', 'Nissan', 'Navara', 2020, 'Galaxy Black', 'Pickup', 'D04-19-100004'),
('FAG9012', 'ENG-441029M', 'CHA-556102938-E', 'Isuzu', 'mu-X', 2017, 'Silky Pearl White', 'SUV', 'E05-20-100005'),
('GHI3456', 'ENG-882910P', 'CHA-334102938-F', 'Suzuki', 'Ertiga', 2022, 'Gray', 'MPV', 'F06-14-100006'),
('VED5561', 'ENG-331029Q', 'CHA-776102938-G', 'Ford', 'Ranger', 2021, 'Arctic White', 'Pickup', 'G07-11-100007'),
('YGA1102', 'ENG-229102R', 'CHA-223102938-H', 'Hyundai', 'Accent', 2016, 'Blue', 'Sedan', 'H08-16-100008'),
('ZXC9981', 'ENG-663019S', 'CHA-664102938-I', 'Kia', 'Seltos', 2020, 'Starbright Yellow', 'SUV', 'I09-17-100009'),
('MAI4451', 'ENG-001928T', 'CHA-001928374-J', 'Mazda', '3', 2019, 'Soul Red', 'Sedan', 'J10-13-100010'),
-- Drivers 11, 13, 14, 16, 17, 18, 20 are skipped (No vehicles)
('CAS5678', 'ENG-7711223', 'CHA-883344556-L', 'Mitsubishi', 'Xpander', 2022, 'Quartz White', 'MPV', 'L12-21-100012'),
('TRE7890', 'ENG-4444556', 'CHA-556677889-O', 'Toyota', 'Fortuner', 2018, 'Attitude Black', 'SUV', 'O15-19-100015'),
('SHA7788', 'ENG-0088990', 'CHA-110011223-S', 'Hyundai', 'Staria', 2023, 'Moonlight Blue', 'Van', 'S19-14-100019'),
-- Drivers 23, 25, 28, 29, 31, 33 are skipped (No vehicles)
('MUN1133', 'ENG-8800112', 'CHA-992233445-U', 'Mitsubishi', 'Montero Sport', 2019, 'Jet Black', 'SUV', 'U21-16-100021'),
('LAO2244', 'ENG-7711224', 'CHA-883344557-V', 'Honda', 'BR-V', 2021, 'Premium Sunline', 'SUV', 'V22-17-100022'),
('ILO4466', 'ENG-5533446', 'CHA-665566779-X', 'Suzuki', 'Jimny', 2022, 'Kinetic Yellow', 'SUV', 'X24-19-100024'),
('CEB6688', 'ENG-3355668', 'CHA-447788991-Z', 'Geely', 'Coolray', 2021, 'Vermilion', 'SUV', 'Z26-15-100026'),
('ANT7799', 'ENG-2266779', 'CHA-338899002-A', 'MG', 'ZS', 2020, 'Laser Blue', 'SUV', 'A27-14-100027'),
('DAV2233', 'ENG-9999002', 'CHA-001122335-D', 'Toyota', 'Raize', 2022, 'Turquoise', 'SUV', 'D30-11-100030'),
('TAR4455', 'ENG-7711225', 'CHA-883344558-F', 'Honda', 'HR-V', 2023, 'Ignite Red', 'SUV', 'F32-18-100032'),
('BAD6677', 'ENG-5533447', 'CHA-665566780-H', 'Isuzu', 'Traviz', 2021, 'White', 'Light Truck', 'H34-16-100034'),
('OBA778',  'ENG-4444558', 'CHA-556677891-I', 'Suzuki', 'S-Presso', 2020, 'Sizzle Orange', 'Hatchback', 'I35-15-100035'),
-- Drivers 37, 42, 45 are skipped (No vehicles)
('LAP8899', 'ENG-3355669', 'CHA-447788992-J', 'Toyota', 'Avanza', 2018, 'Champagne', 'MPV', 'J36-21-100036'),
('BAJ1122', 'ENG-1177891', 'CHA-229900114-L', 'Hyundai', 'Creta', 2022, 'Magnetic Silver', 'SUV', 'L38-23-100038'),
('BON2233', 'ENG-0088992', 'CHA-110011225-M', 'Kia', 'Stonic', 2021, 'Flash Yellow', 'SUV', 'M39-24-100039'),
('BAL3344', 'ENG-9999003', 'CHA-001122336-N', 'Toyota', 'Corolla Cross', 2022, 'Platinum White', 'SUV', 'N40-25-100040'),
('MAL4455', 'ENG-8800114', 'CHA-992233447-O', 'Mitsubishi', 'Strada', 2019, 'Graphite Gray', 'Pickup', 'O41-11-100041'),
('PAS6677', 'ENG-6622337', 'CHA-774455670-Q', 'Nissan', 'Sylphy', 2016, 'Ebony', 'Sedan', 'Q43-13-100043'),
('DAN7788', 'ENG-5533448', 'CHA-665566781-R', 'Suzuki', 'Carry', 2021, 'White', 'Light Truck', 'R44-14-100044'),
('MAL9900', 'ENG-3355670', 'CHA-447788993-T', 'Subaru', 'Forester', 2020, 'Crystal Black', 'SUV', 'T46-16-100046'),
('BFH1122', 'ENG-2266781', 'CHA-338899004-U', 'Volkswagen', 'Santana', 2019, 'Polar White', 'Sedan', 'U47-17-100047'),
('IRI2233', 'ENG-1177892', 'CHA-229900115-V', 'GAC', 'GS4', 2021, 'Lightning Blue', 'SUV', 'V48-18-100048'),
('LIP3344', 'ENG-0088993', 'CHA-110011226-W', 'Foton', 'Gratour', 2018, 'Silver', 'Van', 'W49-19-100049'),
('SJU4455', 'ENG-9999004', 'CHA-001122337-X', 'BMW', '3 Series', 2021, 'Alpine White', 'Sedan', 'X50-20-100050');

-- ========================================================
-- CREATE AND POPULATE: VEHICLE REGISTRATION TABLE
-- ========================================================
CREATE TABLE `vehicle_registrations` (
  registration_number VARCHAR(15) PRIMARY KEY NOT NULL,
  registration_date DATE NOT NULL,
  expiration_date DATE NOT NULL, 
  registration_status ENUM('Active', 'Expired', 'Suspended') NOT NULL DEFAULT 'Active',
  plate_number VARCHAR(7) NOT NULL,
  CONSTRAINT chk_registration_lifetime CHECK (expiration_date > registration_date),
  CONSTRAINT fk_registration_vehicle FOREIGN KEY (plate_number) REFERENCES vehicles (plate_number) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO vehicle_registrations (registration_number, registration_date, expiration_date, registration_status, plate_number) VALUES
('CR-2019-109283', '2025-05-15', '2026-05-15', 'Active', 'ABC1234'),
('CR-2021-992019', '2025-11-22', '2026-11-22', 'Active', 'XYZ7890'),
('CR-2018-445102', '2025-04-18', '2026-04-18', 'Expired', 'NEB4561'),
('CR-2020-773612', '2025-08-04', '2026-08-04', 'Active', 'NCP8822'),
('CR-2017-556102', '2025-09-09', '2026-09-09', 'Active', 'FAG9012'),
('CR-2022-334102', '2025-11-11', '2026-11-11', 'Active', 'GHI3456'),
('CR-2021-776102', '2025-07-07', '2026-07-07', 'Active', 'VED5561'),
('CR-2016-223102', '2025-01-28', '2026-01-28', 'Expired', 'YGA1102'),
('CR-2020-664102', '2025-04-26', '2026-04-26', 'Expired', 'ZXC9981'),
('CR-2019-001928', '2025-09-24', '2026-09-24', 'Active', 'MAI4451'),
('CR-2022-883344', '2025-10-10', '2026-10-10', 'Active', 'CAS5678'),
('CR-2018-556677', '2025-12-04', '2026-12-04', 'Active', 'TRE7890'),
('CR-2023-110011', '2025-09-09', '2026-09-09', 'Active', 'SHA7788'),
('CR-2019-992233', '2025-08-04', '2026-08-04', 'Active', 'MUN1133'),
('CR-2021-883345', '2025-09-11', '2026-09-11', 'Active', 'LAO2244'),
('CR-2022-665567', '2025-11-05', '2026-11-05', 'Active', 'ILO4466'),
('CR-2021-447789', '2025-11-11', '2026-11-11', 'Active', 'CEB6688'),
('CR-2020-338890', '2025-12-14', '2026-12-14', 'Active', 'ANT7799'),
('CR-2022-001123', '2025-03-28', '2026-03-28', 'Expired', 'DAV2233'),
('CR-2023-883346', '2025-02-08', '2026-02-08', 'Expired', 'TAR4455'),
('CR-2021-665568', '2025-10-23', '2026-10-23', 'Active', 'BAD6677'),
('CR-2020-556679', '2025-09-05', '2026-09-05', 'Active', 'OBA778'),
('CR-2018-447790', '2025-06-15', '2026-06-15', 'Active', 'LAP8899'),
('CR-2022-229902', '2025-03-13', '2026-03-13', 'Expired', 'BAJ1122'),
('CR-2021-110013', '2025-09-22', '2026-09-22', 'Active', 'BON2233'),
('CR-2022-001124', '2025-04-28', '2026-04-28', 'Expired', 'BAL3344'),
('CR-2019-992235', '2025-06-14', '2026-06-14', 'Active', 'MAL4455'),
('CR-2016-774458', '2025-08-24', '2026-08-24', 'Active', 'PAS6677'),
('CR-2021-665569', '2025-03-30', '2026-03-30', 'Expired', 'DAN7788'),
('CR-2020-447791', '2025-09-24', '2026-09-24', 'Active', 'MAL9900'),
('CR-2019-338892', '2025-10-31', '2026-10-31', 'Active', 'BFH1122'),
('CR-2021-229903', '2025-05-21', '2026-05-21', 'Active', 'IRI2233'),
('CR-2018-110014', '2025-11-03', '2026-11-03', 'Active', 'LIP3344'),
('CR-2021-001125', '2025-04-19', '2026-04-19', 'Expired', 'SJU4455');

-- ========================================================
-- CREATE AND POPULATE: TRAFFIC VIOLATION TABLE
-- ========================================================
CREATE TABLE `traffic_violations` (
   violation_id INT AUTO_INCREMENT PRIMARY KEY,
   top_number VARCHAR(20) UNIQUE NOT NULL CHECK (top_number REGEXP '^[A-Z]-[0-9]{6}-[0-9]{7}$'),
   violation_type VARCHAR(100) NOT NULL,
   violation_date DATETIME NOT NULL,
   location VARCHAR(100) NOT NULL,
   apprehending_officer VARCHAR(100) NOT NULL,
   violation_status ENUM('Unpaid', 'Paid', 'Contested') NOT NULL DEFAULT 'Unpaid',
   fine_amount INT NOT NULL CHECK (fine_amount >= 0),
   license_number VARCHAR(15) NOT NULL,
   plate_number VARCHAR(7), -- Intentionally allowed to be NULL for drivers without vehicles
   CONSTRAINT fk_violation_driver FOREIGN KEY (license_number) REFERENCES drivers (license_number) ON DELETE RESTRICT,
   CONSTRAINT fk_violation_vehicle FOREIGN KEY (plate_number) REFERENCES vehicles (plate_number) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO traffic_violations (top_number, violation_type, violation_date, location, apprehending_officer, violation_status, fine_amount, license_number, plate_number) VALUES
('T-260518-0000001', 'Reckless Driving', '2026-05-01 08:30:00', 'EDSA Kamuning, Quezon City', 'Officer P. Corpuz', 'Unpaid', 2000, 'A01-15-100001', 'ABC1234'),
('T-260518-0000002', 'Speeding', '2026-05-01 10:15:00', 'C5 Bagong Ilog, Pasig City', 'Officer M. De Leon', 'Paid', 1500, 'B02-18-100002', 'XYZ7890'),
('T-260518-0000003', 'Illegal Parking', '2026-05-02 14:20:00', 'Roxas Blvd, Ermita, Manila', 'Officer J. Santos', 'Unpaid', 1000, 'C03-12-100003', 'NEB4561'),
('T-260518-0000004', 'No Contact Apprehension - Lane Straddling', '2026-05-02 16:45:00', 'McArthur Highway, San Fernando, Pampanga', 'System Camera 04', 'Contested', 500, 'D04-19-100004', 'NCP8822'),
('T-260518-0000005', 'Obstruction', '2026-05-03 09:00:00', 'España Blvd, Sampaloc, Manila', 'Officer R. Agoncillo', 'Paid', 1000, 'E05-20-100005', 'FAG9012'),
('T-260518-0000006', 'Disregarding Traffic Sign', '2026-05-03 11:30:00', 'Real St, Tacloban City', 'Officer L. Gatchalian', 'Unpaid', 1000, 'F06-14-100006', 'GHI3456'),
('T-260518-0000007', 'Invalid Registration', '2026-05-04 13:10:00', 'Magsaysay Ave, Naga City', 'Officer S. Trillanes', 'Paid', 3000, 'G07-11-100007', 'VED5561'),
('T-260518-0000008', 'Not Wearing Seatbelt', '2026-05-04 15:55:00', 'N. Bacalso Ave, Cebu City', 'Officer K. Pimentel', 'Unpaid', 1000, 'H08-16-100008', 'YGA1102'),
('T-260518-0000009', 'Over-speeding', '2026-05-05 07:45:00', 'Marcos Highway, Antipolo, Rizal', 'Officer E. Ejercito', 'Paid', 2000, 'I09-17-100009', 'ZXC9981'),
('T-260518-0000010', 'Number Coding Violation', '2026-05-05 10:00:00', 'Quintin Paredes St, Binondo, Manila', 'Officer B. Benitez', 'Paid', 500, 'J10-13-100010', 'MAI4451'),
-- Plate set to NULL because these drivers no longer own vehicles in the dataset:
('V-260518-0000011', 'Driving with Expired License', '2026-05-06 11:22:00', 'Commonwealth Ave, Quezon City', 'Officer F. Cayetano', 'Unpaid', 3000, 'K11-22-100011', NULL),
('V-260518-0000012', 'Reckless Driving', '2026-05-06 14:35:00', 'Aguinaldo Highway, Silang, Cavite', 'Officer D. Remulla', 'Paid', 2000, 'L12-21-100012', 'CAS5678'),
('V-260518-0000013', 'Illegal Turn', '2026-05-07 08:12:00', 'MacArthur Highway, Valenzuela', 'Officer T. Gatchalian', 'Unpaid', 1500, 'M13-23-100013', NULL),
('V-260518-0000014', 'Disregarding Traffic Sign', '2026-05-07 16:18:00', 'A. Regidor St, Sta. Cruz, Laguna', 'Officer M. Laurel', 'Contested', 1000, 'N14-15-100014', NULL),
('V-260518-0000015', 'Speeding', '2026-05-08 09:40:00', 'Governor Drive, Trece Martires, Cavite', 'Officer G. Revilla', 'Paid', 1500, 'O15-19-100015', 'TRE7890'),
('V-260518-0000016', 'Obstruction', '2026-05-08 13:05:00', 'Calle Crisologo, Vigan City', 'Officer S. Singson', 'Unpaid', 1000, 'P16-18-100016', NULL),
('V-260518-0000017', 'Not Wearing Seatbelt', '2026-05-09 10:50:00', 'Rizal Ave, Olongapo City', 'Officer J. Gordon', 'Paid', 1000, 'Q17-20-100017', NULL),
('V-260518-0000018', 'Reckless Driving', '2026-05-09 15:15:00', 'Purok Maligaya Main Rd, General Santos', 'Officer R. Santos', 'Unpaid', 2000, 'R18-12-100018', NULL),
('V-260518-0000019', 'Illegal Parking', '2026-05-10 11:00:00', 'Shaw Blvd, Mandaluyong City', 'Officer N. Abalos', 'Paid', 1000, 'S19-14-100019', 'SHA7788'),
('V-260518-0000020', 'Overloading', '2026-05-10 14:25:00', 'Daang Maharlika, Tagum City', 'Officer V. Angara', 'Paid', 2500, 'T20-11-100020', NULL),
('A-102938-1122334', 'Speeding', '2026-05-11 08:35:00', 'Madrigal Ave, Alabang, Muntinlupa', 'Officer J. Binay', 'Unpaid', 1500, 'U21-16-100021', 'MUN1133'),
('A-102938-1122335', 'Disregarding Traffic Sign', '2026-05-11 13:40:00', 'Rizal St, Laoag City', 'Officer R. Fariñas', 'Paid', 1000, 'V22-17-100022', 'LAO2244'),
('A-102938-1122336', 'Obstruction', '2026-05-11 16:00:00', 'Samson Road, Caloocan City', 'Officer M. Malapitan', 'Unpaid', 1000, 'W23-18-100023', NULL),
('A-102938-1122337', 'Not Wearing Helmet', '2026-05-12 09:15:00', 'General Luna St, Iloilo City', 'Officer J. Trenas', 'Paid', 1500, 'X24-19-100024', 'ILO4466'),
('A-102938-1122338', 'Illegal Parking', '2026-05-12 11:45:00', 'Mabini St, Lipa City', 'Officer R. Recto', 'Unpaid', 1000, 'Y25-20-100025', NULL),
('A-102938-1122339', 'Reckless Driving', '2026-05-12 15:30:00', 'Gorordo Ave, Lahug, Cebu City', 'Officer T. Osmeña', 'Contested', 2000, 'Z26-15-100026', 'CEB6688'),
('A-102938-1122340', 'Number Coding Violation', '2026-05-13 10:10:00', 'Sumulong Highway, Antipolo, Rizal', 'Officer C. Ynares', 'Paid', 500, 'A27-14-100027', 'ANT7799'),
('A-102938-1122341', 'Disregarding Traffic Sign', '2026-05-13 14:00:00', 'Don A. Velez St, Cagayan de Oro', 'Officer O. Moreno', 'Unpaid', 1000, 'B28-13-100028', NULL),
('A-102938-1122342', 'Speeding', '2026-05-13 16:50:00', 'Katipunan Ave, Quezon City', 'Officer H. Belmonte', 'Paid', 1500, 'C29-12-100029', NULL),
('A-102938-1122343', 'No Helmet', '2026-05-14 08:20:00', 'McArthur Highway, Matina, Davao City', 'Officer S. Duterte', 'Unpaid', 1500, 'D30-11-100030', 'DAV2233'),
('C-881920-5544331', 'Overloading', '2026-05-14 11:05:00', 'Maharlika Highway, Oas, Albay', 'Officer Al Bichara', 'Paid', 2500, 'E31-19-100031', NULL),
('C-881920-5544332', 'Illegal Turn', '2026-05-14 13:55:00', 'McArthur Highway, Tarlac City', 'Officer V. Yap', 'Paid', 1500, 'F32-18-100032', 'TAR4455'),
('C-881920-5544333', 'Obstruction', '2026-05-15 09:30:00', 'Burgos St, Cabanatuan City', 'Officer J. Vergara', 'Unpaid', 1000, 'G33-17-100033', NULL),
('C-881920-5544334', 'Not Wearing Seatbelt', '2026-05-15 11:15:00', 'National Road, Badoc, Ilocos Norte', 'Officer M. Marcos', 'Paid', 1000, 'H34-16-100034', 'BAD6677'),
('C-881920-5544335', 'Speeding', '2026-05-15 15:40:00', 'National Highway, Barrio Barretto, Olongapo', 'Officer R. Paulino', 'Unpaid', 1500, 'I35-15-100035', 'OBA778'),
('C-881920-5544336', 'Disregarding Traffic Sign', '2026-05-16 08:45:00', 'Luna St, La Paz, Iloilo City', 'Officer J. Mabilog', 'Paid', 1000, 'J36-21-100036', 'LAP8899'),
('C-881920-5544337', 'Illegal Parking', '2026-05-16 10:20:00', 'Arnaiz Ave, Makati City', 'Officer R. Junjun', 'Unpaid', 1000, 'K37-22-100037', NULL),
('C-881920-5544338', 'Reckless Driving', '2026-05-16 14:10:00', 'J.P. Laurel Ave, Bajada, Davao City', 'Officer R. Duterte', 'Paid', 2000, 'L38-23-100038', 'BAJ1122'),
('C-881920-5544339', 'Obstruction', '2026-05-16 16:30:00', 'Maysilo Circle, Mandaluyong City', 'Officer B. Abalos', 'Contested', 1000, 'M39-24-100039', 'BON2233'),
('C-881920-5544340', 'Not Wearing Seatbelt', '2026-05-17 09:05:00', 'Rizal St, Baler, Aurora', 'Officer J. Angara', 'Paid', 1000, 'N40-25-100040', 'BAL3344'),
('E-445102-9988771', 'Speeding', '2026-05-17 11:50:00', 'McArthur Highway, Malolos, Bulacan', 'Officer C. Alvarado', 'Unpaid', 1500, 'O41-11-100041', 'MAL4455'),
('E-445102-9988772', 'Illegal Turn', '2026-05-17 13:15:00', 'Poblacion Road, Baliuag, Bulacan', 'Officer R. Roman', 'Paid', 1500, 'P42-12-100042', NULL),
('E-445102-9988773', 'Number Coding Violation', '2026-05-17 15:45:00', 'C5 Road, Ortigas, Pasig City', 'Officer V. Eusebio', 'Unpaid', 500, 'Q43-13-100043', 'PAS6677'),
('E-445102-9988774', 'Disregarding Traffic Sign', '2026-05-18 07:30:00', 'Danao City Public Market Rd, Cebu', 'Officer R. Durano', 'Paid', 1000, 'R44-14-100044', 'DAN7788'),
('E-445102-9988775', 'Obstruction', '2026-05-18 09:10:00', 'Marcos Highway, Antipolo, Rizal', 'Officer L. Gatlabayan', 'Paid', 1000, 'S45-15-100045', NULL),
('E-445102-9988776', 'Speeding', '2026-05-18 10:40:00', 'Poblacion Highway, Malasiqui, Pangasinan', 'Officer Am Espino', 'Unpaid', 1500, 'T46-16-100046', 'MAL9900'),
('E-445102-9988777', 'Illegal Parking', '2026-05-18 11:20:00', 'Sucat Road, Parañaque City', 'Officer E. Olivarez', 'Paid', 1000, 'U47-17-100047', 'BFH1122'),
('E-445102-9988778', 'Not Wearing Seatbelt', '2026-05-18 13:00:00', 'Highway Proper, Iriga City', 'Officer M. Madrigal', 'Unpaid', 1000, 'V48-18-100048', 'IRI2233'),
('E-445102-9988779', 'Disregarding Traffic Sign', '2026-05-18 14:15:00', 'Ayala Highway, Lipa City, Batangas', 'Officer E. Sabili', 'Paid', 1000, 'W49-19-100049', 'LIP3344'),
('E-445102-9988780', 'Obstruction', '2026-05-18 15:00:00', 'N. Domingo St, San Juan City', 'Officer J. Ejercito', 'Unpaid', 1000, 'X50-20-100050', 'SJU4455');

-- Re-enable key checks to protect production data integrity
SET FOREIGN_KEY_CHECKS = 1;