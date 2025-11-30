# **SWATS V0.01 Prototype Task List (Micro-Granular TDD)**

**Scope:** V0.01 Walking Skeleton  
**Methodology:** Strict Test-Driven Development (Red-Green-Refactor)  
**Stack:** Flask, SQLAlchemy, Pytest

## **1. Project Initialization & Infrastructure**

* **Environment Setup**
  * [x] Initialize Git repository & `.gitignore`.
  * [x] Configure `requirements.txt` (substituted for `pyproject.toml`) with dependencies: `flask`, `sqlalchemy`, `psycopg2-binary`, `bcrypt`, `pyjwt`, `pandas`.
  * [x] Install dev tools: `pytest`, `pytest-cov`, `black`, `flake8`.
* **Scaffolding**
  * [x] Create folder structure: `src/{api, core, models, services, utils}` and `tests/{unit, integration}`.
  * [ ] **(Green)** Implement `src/core/config.py` (Database URL, Secret Keys).
  * [x] **(Green)** Implement `src/core/database.py` (SQLAlchemy `db` instance).
  * [ ] **(Green)** Create `tests/conftest.py` with `db_session` fixture (SQLite memory).

## **1.5. Service Orchestration (Day 3)**

* **Dependency Injection**
  * [x] **(Red)** Create `tests/unit/test_container.py`: Test Service/Repo wiring.
  * [x] **(Green)** Implement `src/container.py`: DI Container class.
  * [x] **(Green)** Implement `src/app.py`: App factory with Container initialization.

## **2. Database Layer (The Schema)**

* **User & Student Models**
  * [x] **(Red)** Create `tests/unit/test_models.py`: Test `User` creation and password hashing logic.
  * [x] **(Green)** Implement `src/models/user.py`: `User` model (id, username, role, hash).
  * [x] **(Green)** Implement `src/models/student.py`: `Student` model (FK `user_id`, `risk_score`, `misses`).
  * [ ] **(Refactor)** Add SQLAlchemy relationships (User $\leftrightarrow$ Student).
* **Academic Structure Models**
  * [x] **(Green)** Implement `src/models/course.py`: `Course` model (FK `director_id`).
  * [x] **(Green)** Implement `src/models/module.py`: `Module` model.
  * [x] **(Green)** Implement `src/models/enrollment.py`: `StudentModule` association table.
* **Data Models**
  * [x] **(Green)** Implement `src/models/survey.py`: `WellbeingSurvey` (stress, sleep, status).
  * [x] **(Green)** Implement `src/models/academic.py`: `ModuleGrade` and `AttendanceRegister`.
  * [ ] **(Green)** Run `alembic revision --autogenerate` to create the initial migration.

## **3. Authentication & Core Logic**

* **Auth Service**
  * [x] **(Red)** Create `tests/unit/test_auth_service.py`: Test login with valid/invalid credentials.
  * [x] **(Green)** Implement `src/services/auth_service.py`: `authenticate_user` returning JWT.
  * [x] **(Green)** Implement `src/api/auth.py`: `POST /login` endpoint.
* **Utility: Password Reversal**
  * [ ] **(Red)** Create `tests/unit/test_utils.py`: Test `generate_default_password("alice")` returns `"ecila"`.
  * [ ] **(Green)** Implement `src/utils/security.py`: Password generation logic.

## **4. Data Ingestion (Officer Features)**

* **User Import (CSV)**
  * [x] **(Red)** Create `tests/integration/test_import_users.py`: Upload CSV $\rightarrow$ Assert Users & Students created.
  * [x] **(Green)** Implement `src/services/import_service.py`: `process_user_csv` (Parsing & DB Insert).
  * [x] **(Green)** Implement `src/api/admin.py`: `POST /import/users` endpoint.
* **Academic Data Import**
  * [x] **(Red)** Create `tests/integration/test_import_academic.py`: Upload Grades CSV $\rightarrow$ Assert `ModuleGrade` updated.
  * [x] **(Green)** Implement `src/services/import_service.py`: `process_academic_csv` (Grades/Attendance).
  * [x] **(Green)** Implement `src/api/admin.py`: `POST /import/academic` endpoint.
* **Hard Delete (GDPR)**
  * [ ] **(Red)** Create `tests/system/test_cascade_delete.py`: Create User+Data $\rightarrow$ Delete User $\rightarrow$ Assert all data gone.
  * [ ] **(Green)** Implement `src/services/admin_service.py`: `hard_delete_user` (Ensure Cascade configuration in Models).

## **5. Wellbeing Surveys (Student Features)**

* **Submission Logic**
  * [ ] **(Red)** Create `tests/unit/test_survey.py`: Submit Stress=5 $\rightarrow$ Assert DB record created.
  * [ ] **(Green)** Implement `src/api/surveys.py`: `POST /submit`.
* **Skip Logic (The Penalty)**
  * [ ] **(Red)** Add test to `test_survey.py`: Call skip $\rightarrow$ Assert `status=SKIPPED` AND `student.consecutive_misses` increments.
  * [ ] **(Green)** Implement `src/services/survey_service.py`: `skip_survey` logic.
  * [ ] **(Green)** Connect to `src/api/surveys.py`: `POST /skip`.

## **6. The Risk Engine (Algorithm)**

* **Calculation Logic**
  * [x] **(Red)** Create `tests/unit/test_risk_engine.py`:
    * Test 1: High Stress (5) + Low Sleep (2) = High Risk.
    * Test 2: High Misses (5) adds 12.5 points (50/4).
    * Test 3: High Grade (100) lowers risk.
    * **Formula:** `Risk = (Stress*20 + (100-Sleep*8) + Misses*10 + (100-Grade)) / 4`
    * [x] **(Green)** Implement `src/services/risk_engine.py`: `calculate_risk(student)` function.
* **Integration**
  * [ ] **(Refactor)** Trigger `calculate_risk` automatically when Analytics endpoints are called (On-Demand).

## **7. Dual-Privacy Analytics (The Core Value)**

* **Privacy Hashing**
  * [ ] **(Red)** Create `tests/unit/test_privacy.py`: Test `hash_id("123")` returns consistent hash, distinct from input.
  * [ ] **(Green)** Implement `src/utils/privacy.py`: SHA-256 or similar hashing wrapper.
* **Director View (Anonymized)**
  * [x] **(Red)** Create `tests/integration/test_director_view.py`:
    * Authenticate as Director.
    * Assert response list has `hashed_id`.
    * Assert `name`/`email` are `None`.
  * [x] **(Green)** Implement `src/services/analytics_service.py`: `get_director_data` (Filter by Course + Apply Hash).
    * [x] **(Green)** Implement `src/api/analytics.py`: `GET /director`.
* **Officer View (Unanonymized)**
  * [x] **(Red)** Create `tests/integration/test_officer_view.py`:
    * Authenticate as Officer.
    * Assert response list has real `first_name`, `last_name`.
  * [x] **(Green)** Implement `src/services/analytics_service.py`: `get_officer_snapshot`.
  * [x] **(Green)** Implement `src/api/analytics.py`: `GET /officer/snapshot`.
* **Officer Diagnostic (Trends)**
  * [x] **(Red)** Add test: `get_student_history` returns chronological Stress/Sleep lists.
  * [x] **(Green)** Implement `src/services/analytics_service.py`: `get_student_detail`.
  * [x] **(Green)** Implement `src/api/analytics.py`: `GET /officer/student/<id>`.

## **8. UI & Frontend (Templates)**

* **Basic Views**
  * [ ] **(Green)** Create `templates/login.html`.
  * [x] **(Green)** Create `templates/student_survey.html` (Form + Skip Button).
  * [x] **(Green)** Create `templates/officer_dashboard.html` (Table with Risk Highlighting).
  * [x] **(Green)** Create `templates/director_dashboard.html` (Anonymized Table).
* **Wiring**
  * [ ] **(Green)** Create `src/api/views.py`: Render templates and connect to API endpoints via AJAX or Form Submit.

## **9. Final Verification**

* **E2E Testing**
  * [x] **(Red)** Create `tests/e2e/test_full_flow.py`:
      1. Officer Imports User `Alice`.
      2. Alice logins (`ecila`), Skips Survey.
      3. Officer Imports Grade (40%).
      4. Director checks view (Sees Hashed ID, Risk > 50).
      5. Officer checks view (Sees "Alice", Risk > 50).
  * [x] **(Green)** Run full suite `pytest`.
