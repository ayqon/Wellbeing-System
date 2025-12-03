# SWATS — Student Wellbeing & Attendance Tracking System  
**Version:** V0.1 (Prototype / Work in Progress)    
**Status:** Active Development

## 📘 Overview

SWATS is an early-warning and wellbeing monitoring system currently under development.  
This V0.1 prototype focuses on establishing the **core architecture**, **domain models**,  
and a **minimum walking skeleton** that the team will expand in future iterations.

The project aims to provide:

- Daily wellbeing surveys for students  
- A dynamic risk-scoring engine  
- Separate dashboards for Directors (anonymised) and Officers (full detail)  
- CSV import pipelines for students, grades, and attendance  
- A secure, modular backend built using strict OOP principles  

## 👥 Team Members

| Role | Developer | Responsibility |
|------|-----------|----------------|
| **DEV1** | Muhammad Ibne Muzammil | Infrastructure, DI Container, Architecture |
| **DEV2** | Ioannis Konstantinou | User Domain, Auth Logic |
| **DEV3** | Mohammad Irfan Mohammad Noor | Student & Tracking Models |
| **DEV4** | Wu Zheyu | Academic Models, CSV Parsers |
| **DEV5** | Paul Ayan | Risk Engine, Service Logic |
| **DEV6** | Zhang Zhexian | Privacy Layer, Analytics Design |

## 🔐 User Roles

| Actor | Access Level | Responsibilities |
| :--- | :--- | :--- |
| **Student** | Basic | Log in, Submit Wellbeing Surveys, Skip Surveys (with penalty). |
| **Officer** | **Super Admin** | Import Users/Data (CSV), Hard Delete Users, View **Unanonymized** Risk Data & Historical Trends. |
| **Director** | Restricted | View **Anonymized** Risk & Academic Analytics (Hash-masked IDs) for their course. |

## 🚀 Key Features (v0.1)

### 1. Director Academic Charts
The Director Dashboard includes advanced visualizations for academic performance:
-   **Scatter Plot**: "Performance vs Attendance" - Correlates student grades with attendance percentages.
-   **Histogram**: "Average Grade by Module" - Shows the distribution of grades across different modules.
-   **Privacy**: All data remains anonymized (hashed IDs) to comply with privacy requirements.

### 2. Student Radar Chart
The Student Dashboard features a **Wellbeing Radar Chart**:
-   **Visualizes**: Stress, Sleep, Attendance, and Grades.
-   **Comparison**: Overlays the student's metrics against the **Cohort Average**.
-   **Goal**: Provides immediate visual feedback on areas needing attention.

### 3. Dynamic Officer Analytics
The Officer Dashboard features a fully dynamic analytics tool:
-   **Customizable Axes**: Select X and Y axes from **Grades**, **Attendance**, **Sleep**, and **Stress**.
-   **Clustering**: Group students by performance/wellbeing bands (e.g., "Fail", "First", "Critical Attendance").
-   **Interactive Filtering**: Toggle specific clusters on/off to focus on at-risk groups.

### 4. Expanded Data Import
The Admin interface supports granular CSV imports:
-   **Users**: Bulk create students and staff.
-   **Grades**: Import module results.
-   **Attendance**: Import session registers.
-   **Surveys**: Import historical wellbeing data.

### 5. Algorithmic Risk Engine
Calculates a dynamic risk score (0-100) based on weighted factors:
-   **Stress** (Self-reported)
-   **Sleep** (Self-reported)
-   **Attendance** (System tracked)
-   **Grades** (System tracked)
-   **Missed Surveys** (Penalty factor)

## 🛠️ Setup & Installation

### Prerequisites
-   Python 3.10+
-   pip

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd wellbeing-system
    ```

2.  **Create a virtual environment** (Recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Initialize the database** (First run only):
    The application uses SQLite. The database is initialized automatically on first run, or you can use the import tools to seed data.

2.  **Start the server**:
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

3.  **Seed the Database** (Optional):
    Populate the database with synthetic test data (Users, Students, Grades, Attendance, Surveys):
    ```bash
    python -m src.seed
    ```
    *Note: This will reset the database and create default users (e.g., `admin`, `director`, `officer`).*

### Running Tests

The project maintains **100% Test Coverage**. To run the test suite:

1.  **Run all tests**:
    ```bash
    pytest
    ```

2.  **Run with coverage report**:
    ```bash
    pytest --cov=src --cov-report=term-missing
    ```

## 🏗️ Architecture

The system follows a **Monolithic MVC** architecture with a strict separation of concerns:

-   **`src/models`**: SQLAlchemy ORM models (Data Layer).
-   **`src/repositories`**: Data access abstraction.
-   **`src/services`**: Business logic and orchestration.
-   **`src/api`**: Flask Blueprints (Controllers).
-   **`src/templates`**: Jinja2 HTML templates (View).
-   **`src/container.py`**: Dependency Injection container.

See `ARCHITECTURE.md` for detailed diagrams and design decisions.
