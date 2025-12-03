# Codebase Documentation

This document provides a comprehensive technical overview of the Student Wellbeing & Academic Tracking System (SWATS). It details the file structure, core components, data models, services, and API endpoints.

## 1. File Structure

```
src/
├── api/                    # API Route Blueprints
│   ├── admin.py            # Admin management routes
│   ├── analytics.py        # Analytics and dashboard routes
│   ├── auth.py             # Authentication routes
│   └── surveys.py          # Student survey routes
├── core/                   # Core infrastructure
│   └── database.py         # Database connection and session handling
├── dtos/                   # Data Transfer Objects
│   ├── risk_report_dto.py
│   ├── student_history_dto.py
│   └── student_metrics_dto.py
├── models/                 # SQLAlchemy Data Models
│   ├── academic.py         # Course, Module, Grade, Attendance
│   ├── base.py             # Base model and mixins
│   ├── student.py          # Student entity
│   ├── survey.py           # Wellbeing survey entity
│   ├── system.py           # System configuration
│   └── user.py             # User entity (Auth)
├── repositories/           # Data Access Layer
│   ├── base.py             # Generic Repository implementation
│   ├── student_repository.py
│   ├── survey_repository.py
│   ├── system_repository.py
│   └── user_repository.py
├── services/               # Business Logic Layer
│   ├── admin_service.py    # Admin operations
│   ├── analytics_service.py# Risk analysis and dashboards
│   ├── auth_service.py     # Authentication logic
│   ├── import_service.py   # Data import orchestration
│   ├── risk_engine.py      # Risk calculation algorithm
│   ├── survey_service.py   # Survey management
│   ├── token_service.py    # JWT handling
│   └── user_csv_parser.py  # CSV parsing strategy
├── static/                 # Static Assets
│   ├── css/
│   └── js/
├── templates/              # Jinja2 HTML Templates
├── utils/                  # Utilities
│   ├── parsers.py          # Abstract and concrete parsers
│   └── privacy.py          # Anonymization logic
├── app.py                  # Application Factory
└── container.py            # Dependency Injection Container
```

## 2. Core Components

### `src/app.py`
- **`create_app(config_name)`**: Application factory function. Initializes Flask, configures the app, sets up the Dependency Injection (DI) container, registers blueprints, and initializes Flask-Login.

### `src/container.py`
- **`Container`**: Central Dependency Injection container. Manages the lifecycle of services and repositories, ensuring singletons where appropriate and handling dependency wiring.
    - `user_repository()`, `student_repository()`, etc.: Factory methods for repositories.
    - `auth_service()`, `admin_service()`, `analytics_service()`, etc.: Factory methods for services with injected dependencies.

### `src/core/database.py`
- **`Database`**: Singleton class managing the SQLAlchemy engine and session factory (`SessionLocal`).
    - `get_db()`: Generator for yielding database sessions (useful for dependency injection in routes).

## 3. Data Models (`src/models`)

### `base.py`
- **`BaseModel`**: Abstract base for all models.
- **`TimestampMixin`**: Adds `created_at` and `updated_at` columns.
- **`SoftDeleteMixin`**: Adds `is_active` and `deleted_at` columns and methods (`soft_delete`, `restore`).

### `user.py`
- **`User`**: Represents system users (Student, Officer, Director).
    - Fields: `username`, `password_hash`, `role`, `first_name`, `last_name`.
    - Methods: `set_password()`, `check_password()`.

### `student.py`
- **`Student`**: Represents a student profile.
    - Fields: `student_id` (business ID), `user_id` (FK), `name`, `email`, `missed_surveys`, `course_code`, `current_risk_score`.
    - Methods: `increment_misses()`, `reset_misses()`.

### `academic.py`
- **`Course`**: Academic course (e.g., "Applied AI").
- **`Module`**: Module within a course.
- **`StudentModule`**: Enrollment record.
- **`ModuleGrade`**: Grade record (0-100).
- **`AttendanceRegister`**: Attendance record (Present/Absent).

### `survey.py`
- **`WellbeingSurvey`**: Weekly survey submission.
    - Fields: `week`, `year`, `status` (PENDING/COMPLETED/SKIPPED), `stress` (1-5), `sleep` (0-24), `is_critical`.

### `system.py`
- **`SystemConfig`**: Key-value store for global settings (e.g., academic year dates).

## 4. Repositories (`src/repositories`)

### `base.py`
- **`AbstractRepository`**: Interface defining standard CRUD operations (`add`, `get`, `list`, `update`, `delete`).
- **`SqlAlchemyRepository`**: Generic implementation using SQLAlchemy sessions.

### Specific Repositories
- **`UserRepository`**: Adds `get_by_username()`.
- **`StudentRepository`**: Adds `get_by_student_id()`, `fetch_by_course()`.
- **`SurveyRepository`**: Adds `get_by_student_week()`, `get_by_student()`.
- **`SystemRepository`**: Adds `get(key)`.

## 5. Services (`src/services`)

### `AuthService`
- **`login(username, password)`**: Authenticates user and returns JWT.

### `AdminService`
- **`create_user(...)`**: Creates a new user with hashed password.
- **`hard_delete_user(user_id)`**: Permanently deletes a user and cascades to related data.
- **`bulk_delete_users(user_ids)`**: Batch deletion with error tracking.
- **`set_academic_year(...)`**: Configures academic year dates.
- **`get_current_academic_week()`**: Calculates current week number based on start date.

### `ImportService`
- **`execute_import(file_stream)`**: Orchestrates import based on file content.
- **`process_user_csv(stream)`**: Parses and imports Users and Students.
- **`process_academic_csv(stream)`**: Parses and imports Grades/Attendance.

### `AnalyticsService`
- **`get_officer_snapshot()`**: Returns risk data for all students (Officer view).
- **`get_director_risk_view(course_id)`**: Returns anonymized, shuffled risk data (Director view).
- **`get_director_academic_view(course_id)`**: Returns unanonymized academic data (Director view).
- **`get_student_history(student_id)`**: Returns chronological wellbeing history DTO.
- **`get_student_metrics_with_cohort(student_id)`**: Returns normalized metrics vs cohort averages for radar charts.

### `SurveyService`
- **`submit_response(...)`**: Validates and saves survey response, checks critical thresholds.
- **`process_skip(...)`**: Marks survey as skipped and increments missed count.

### `RiskCalculator` (`src/services/risk_engine.py`)
- **`compute(metrics)`**: Calculates risk score (0-100) based on Stress, Sleep, Misses, and Grades.

## 6. API Routes (`src/api`)

### `auth.py` (`/auth`)
- `POST /login`: User login.
- `GET /logout`: User logout.

### `admin.py` (`/admin`)
- `GET /users`: List users.
- `GET /users/add`: Add user form.
- `POST /users/create`: Create user action.
- `POST /users/delete`: Delete user action.
- `POST /users/delete-bulk`: Bulk delete action.
- `GET /settings`: System settings form.
- `POST /settings/update`: Update settings action.
- `GET /import`: Import data form.
- `POST /import/users`: Import users CSV.
- `POST /import/academic`: Import academic CSV.

### `analytics.py` (`/analytics`)
- `GET /officer/dashboard`: Officer dashboard view.
- `GET /director/dashboard`: Director dashboard view.
- `GET /student/<id>/detail`: Detailed student view.
- `GET /risk-list`: JSON endpoint for officer data.
- `GET /correlations`: JSON endpoint for director risk data.

### `surveys.py` (`/api/surveys`)
- `GET /dashboard`: Student dashboard (Radar chart).
- `GET /new`: Survey form.
- `POST /submit`: Submit survey JSON.
- `POST /skip`: Skip survey JSON.

## 7. Utilities & DTOs

### `src/utils/parsers.py`
- **`UserCSVParser`**: Parses user/student CSVs.
- **`GradeCSVParser`**: Parses grade CSVs.

### `src/utils/privacy.py`
- **`Anonymizer`**: Hashes user IDs and redacts PII for privacy-preserving views.

### DTOs
- **`StudentMetricsDTO`**: Data structure for risk calculation inputs.
- **`StudentHistoryDTO`**: Data structure for student history view.
