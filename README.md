# 🚗 LTO Information Management System

A full-stack web application for the **Land Transportation Office (LTO)** built with **Streamlit** and **MariaDB**. The system manages driver records, vehicle registrations, traffic violations, and generates operational reports used by LTO personnel.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the App](#running-the-app)
- [Business Reports](#business-reports)
- [Architecture](#architecture)
- [Contributors](#contributors)

---

## Features

- **Driver Management** — Register, search, update, and delete driver records with license tracking
- **Vehicle Management** — Full CRUD for vehicles linked to their registered owners
- **Registration Tracking** — Monitor vehicle registration status and expiration dates
- **Violation Records** — Log traffic violations with fine amounts, officers, and payment status
- **7 Business Reports** — Pre-built filtered queries for operational decision-making
- **Input Validation** — All data is validated (regex, enum, date ordering) before reaching the database
- **SQL Injection Prevention** — All queries use parameterized `?` placeholders
- **Performance Caching** — Read queries are cached with `@st.cache_data` and auto-invalidated on writes

---

## Tech Stack

| Layer     | Technology                                                 |
| --------- | ---------------------------------------------------------- |
| Frontend  | [Streamlit](https://streamlit.io/) (Python)                |
| Backend   | Python 3.10+                                               |
| Database  | [MariaDB](https://mariadb.org/) 10.6+                      |
| DB Driver | [mariadb](https://pypi.org/project/mariadb/) (C connector) |

---

## Project Structure

```
LTO-Information-Management-System/
├── .streamlit/
│   └── secrets.toml            # Database credentials (not committed)
├── requirements.txt            # Python dependencies
├── README.md
└── src/
    ├── dashboard.py            # Streamlit entry point (dashboard)
    ├── pages/                  # Streamlit multi-page UI
    │   ├── 1_Drivers.py
    │   ├── 2_Vehicles.py
    │   ├── 3_Registrations.py
    │   └── 4_Violations.py
    ├── controllers/            # Input validation & routing
    │   ├── driver_controller.py
    │   ├── vehicle_controller.py
    │   ├── registration_controller.py
    │   └── violation_controller.py
    ├── services/               # Business logic & SQL execution
    │   ├── driver_service.py
    │   ├── vehicle_service.py
    │   ├── registration_service.py
    │   └── violation_service.py
    ├── models/                 # Data classes for each entity
    │   ├── driver_model.py
    │   ├── vehicle_model.py
    │   ├── registration_model.py
    │   └── violation_model.py
    ├── db/
    │   ├── db_connection.py    # Connection pool & query executor
    │   ├── query_helpers.py    # WHERE clause builder & validators
    │   └── seed.sql            # Schema + seed data (100 drivers,
    │                           #   120 vehicles, 120 registrations,
    │                           #   200 violations)
    └── queries.sql             # Reference SQL for all 7 reports
```

---

## Prerequisites

1. **Python 3.10+** — [Download](https://www.python.org/downloads/)
2. **MariaDB 10.6+** — [Download](https://mariadb.org/download/)
3. **MariaDB C Connector** — Required by the `mariadb` Python package
   - **macOS:** `brew install mariadb-connector-c`
   - **Ubuntu/Debian:** `sudo apt install libmariadb-dev`
   - **Windows:** Included with the MariaDB MSI installer

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yunaxoxo/LTO-Information-Management-System.git
cd LTO-Information-Management-System
```

### 2. Create & Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

Open a MariaDB shell as root and run the seed script:

```bash
sudo mariadb < src/db/seed.sql
```

This will:

- Create the `lto_system` database
- Create the `lto_admin` user with full privileges
- Create all 4 tables (`drivers`, `vehicles`, `vehicle_registrations`, `traffic_violations`)
- Insert all seed data (100 drivers, 120 vehicles, 120 registrations, 200 violations)

### 5. Configure Credentials

Create the Streamlit secrets file (if it doesn't exist):

```bash
mkdir -p .streamlit
```

Then edit `.streamlit/secrets.toml`:

```toml
[DB_CREDENTIALS]
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "lto_admin"
DB_PASSWORD = "LtoProject2026!"
DB_NAME = "lto_system"
```

> ⚠️ **Do not commit this file.** Make sure `.streamlit/` is in your `.gitignore`.

---

## Running the App

From the project root directory:

```bash
streamlit run src/dashboard.py
```

The app will open in your browser at **http://localhost:8501**.

Use the sidebar to navigate between pages:

- **Drivers** — Manage driver records and run Reports 1 & 4
- **Vehicles** — Manage vehicles and run Reports 2 & 3
- **Registrations** — Track vehicle registration status
- **Violations** — Log violations and run Reports 5, 6 & 7

To stop the server, press `Ctrl+C` in the terminal.

---

## Business Reports

| #   | Report                     | Description                                                       |
| --- | -------------------------- | ----------------------------------------------------------------- |
| 1   | **Filtered Drivers**       | View drivers filtered by license type, status, sex, and age range |
| 2   | **Vehicles by Owner**      | View all vehicles owned by a specific driver                      |
| 3   | **Expired Registrations**  | View vehicles with expired registrations as of a given date       |
| 4   | **Invalid Licenses**       | View all drivers with expired or suspended licenses               |
| 5   | **Violations by Driver**   | View violations for a driver within a date range                  |
| 6   | **Violations by Type**     | View violation counts grouped by type for a date range            |
| 7   | **Violations by Location** | View violations matching a city or region                         |

---

## Architecture

The application follows a **strict layered architecture** with separation of concerns:

```
┌─────────────────────────────────────────┐
│           Streamlit Pages (UI)          │
│         pages/1_Drivers.py, ...         │
├─────────────────────────────────────────┤
│            Controllers                  │
│    Input validation & sanitization      │
├─────────────────────────────────────────┤
│             Services                    │
│   Business logic & parameterized SQL    │
├─────────────────────────────────────────┤
│           Database Layer                │
│   Connection pool & query execution     │
├─────────────────────────────────────────┤
│             MariaDB                     │
│          lto_system database            │
└─────────────────────────────────────────┘
```

- **Pages** → Call controllers, display results with `st.dataframe()`, show messages with `st.success()`/`st.error()`
- **Controllers** → Validate all inputs (regex, enum, types, dates), construct model objects, delegate to services
- **Services** → Execute parameterized SQL, manage caching (`@st.cache_data`), invalidate cache on writes
- **DB Layer** → Connection pooling via `mariadb.ConnectionPool`, auto commit/rollback, dict-based result mapping

---

## Contributors

- _Frendzo Charles Pelagio_
- _Cherrie Joyce Nieto_
- _Rein Matthew Malonzo_
