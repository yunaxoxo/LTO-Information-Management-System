
--DRIVER TABLE WITH VALIDATION
CREATE TABLE DRIVER (
    License_number VARCHAR(20) PRIMARY KEY NOT NULL,
    Full_name VARCHAR(100) NOT NULL,
    Birthday DATE NOT NULL,
    Sex VARCHAR(10) NOT NULL,
    Address VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
    License_type ENUM(
        'Student',
        'Non-Professional',
        'Professional'
    ) NOT NULL,
    License_status VARCHAR(20) NOT NULL,
    License_issuance_date DATE NOT NULL,
    License_expiration_date DATE NOT NULL
);

-- VEHICLE TABLE WITH FOREIGN KEY OF DRIVER 
CREATE TABLE VEHICLE (
    Plate_number VARCHAR(20) PRIMARY KEY NOT NULL,
    Engine_number VARCHAR(30) UNIQUE NOT NULL,
    Chassis_number VARCHAR(30) UNIQUE NOT NULL,
    Model VARCHAR(50) NOT NULL,
    Color VARCHAR(20) NOT NULL,
    Vehicle_type VARCHAR(100) NOT NULL,
    Make VARCHAR(50) NOT NULL,
    Year INT NOT NULL,
    License_number VARCHAR(20) NOT NULL,

    CONSTRAINT fk_vehicle_driver
    FOREIGN KEY (License_number)
    REFERENCES DRIVER (License_number)
);
