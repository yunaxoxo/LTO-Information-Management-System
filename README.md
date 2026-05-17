# MAYLA — Entity Relationship Diagram (ERD)

This document represents the database design for the LTO Information Management System. It defines the core entities, their attributes, and the relationships between them. The goal of this structure is to ensure data integrity, reduce redundancy, and model real-world LTO operations in a structured relational format.

---

# 🧩 Core Entities

## DRIVER

Represents licensed drivers registered in the system.

### Attributes

- License_number (PK)
- Full_name
- First_name
- Middle_name
- Last_name
- Birthday
- Sex
- Address
- Age
- License_type
- License_status
- License_issuance_date
- License_expiration_date

---

## VEHICLE

Represents registered vehicles in the system.

### Attributes

- Plate_number (PK)
- Engine_number
- Chassis_number
- Model
- Color
- Vehicle_type
- Make
- Year
- License_number (FK)

---

## VEHICLE_REGISTRATION

Represents official registration records for vehicles.

### Attributes

- Registration_number (PK)
- Registration_date
- Registration_status
- Expiration_date
- Plate_number (FK)

---

## TRAFFIC_VIOLATION

Represents recorded traffic violations involving drivers and vehicles.

### Attributes

- Violation_id (PK)
- Violation_type
- Date
- Location
- Apprehending_officer
- Violation_status
- Fine_amount
- License_number (FK)
- Plate_number (FK)

---

# 🔗 Entity Relationships

The system models real-world LTO operations using relational connections:

- A **Driver** can own multiple **Vehicles**
- A **Vehicle** can have multiple **Registrations**
- A **Driver** can commit multiple **Traffic Violations**
- A **Vehicle** can be involved in multiple **Traffic Violations**

---

# 📊 Relationship Diagram Overview

```text
DRIVER ──── owns ────> VEHICLE ──── has ────> VEHICLE_REGISTRATION

   │
   └── commits ───> TRAFFIC_VIOLATION <── involved in ─── VEHICLE
```

---

# 🎯 Design Purpose

This ERD is designed to:

- Model real-world LTO processes accurately
- Maintain relational integrity using primary and foreign keys
- Support scalable querying for reporting and analytics
- Reduce data redundancy through normalization
- Serve as the foundation for SQL reporting and backend integration

---

# 🏗️ System Role in the Project

This schema is the **foundation layer** of the entire system:

- Used by Milestone 1 (Database Design)
- Supports all SQL reporting queries (Milestone 2)
- Provides structured data for backend API processing (Milestone 4)

---

# ⚙️ Summary

The ERD defines a clear relational structure between:

- Drivers
- Vehicles
- Registrations
- Traffic Violations

It ensures that the system reflects a real-world transportation management environment while remaining efficient, normalized, and scalable.
