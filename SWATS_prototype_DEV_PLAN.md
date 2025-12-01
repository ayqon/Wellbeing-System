# **Core OOP Principles Applied:**

* **Encapsulation:** All business logic resides within **Service Classes** or **Rich Domain Models**, never in global functions or API routes.
* **Inheritance:** Repositories extend an `AbstractRepository`; Models use `Mixins` for shared behavior (e.g., Soft Delete).
* **Polymorphism:** Parsers implement a common `FileParser` interface.
* **Dependency Injection (DI):** Services receive Repositories via their `__init__` constructor, enabling loose coupling and easier mocking.

---

## **SWATS V0.01: OOP-Driven TDD Plan**

**Architecture:** N-Tier (Controller $\to$ Service $\to$ Repository $\to$ Model).
**Constraint:** Strict File/Class Ownership (No shared edits during the day).

---

### **Day 1: Object Hierarchy & Domain Models**

**Goal:** Define the Entities and Abstract Base Classes (ABCs).

#### **Dev 1 : Infrastructure & Abstractions**

* **Scope:** `src/core/`, `src/models/base.py`
  * [x] **(Task)** Initialize Repo. Push structure.
  * [x] **(Green)** Create `src/core/database.py`: Define `Database` singleton class.
  * [x] **(Green)** Create `src/models/base.py`:
    * Define `BaseModel` (SQLAlchemy Declarative Base).
    * Define `SoftDeleteMixin` class (Encapsulates `is_active` logic).
    * Define `TimestampMixin` class.

#### **Dev 2: User Entity**

* **Scope:** `src/models/user.py`
  * [x] **(Red)** Create `tests/unit/test_user_model.py`. Test `check_password` method.
  * [x] **(Green)** Implement `User` class (Inherits `BaseModel`, `SoftDeleteMixin`).
    * **OOP:** Encapsulate password hashing inside `set_password()` and `check_password()` methods.

#### **Dev 3: Student Entity**

* **Scope:** `src/models/student.py`
  * [x] **(Red)** Create `tests/unit/test_student_model.py`.
  * [x] **(Green)** Implement `Student` class (Inherits `BaseModel`).
    * **OOP:** Add method `increment_misses()` to encapsulate counter logic.

#### **Dev 4: Academic Hierarchy**

* **Scope:** `src/models/academic.py`
  * [x] **(Red)** Create `tests/unit/test_academic_models.py`.
  * [x] **(Green)** Implement `Course` and `Module` classes.
  * [x] **(Green)** Implement `StudentModule` (Association Object Pattern).

#### **Dev 5: Tracking Entities**

* **Scope:** `src/models/tracking.py`
  * [x] **(Red)** Create `tests/unit/test_tracking_models.py`.
  * [x] **(Green)** Implement `WellbeingSurvey` class.
    * **OOP:** Add property `is_critical` (returns Bool) based on stress level.
  * [x] **(Green)** Implement `ModuleGrade` and `AttendanceRegister` classes.

#### **Dev 6: Privacy Object**

* **Scope:** `src/utils/privacy.py`
  * [x] **(Red)** Create `tests/unit/test_anonymizer.py`.
  * [x] **(Green)** Implement `Anonymizer` class.
    * **OOP:** Method `mask_identity(user_id: str) -> str`. Make the salt a private attribute `_salt`.

**🌙 Nightly Refactor (Dev 1):**

> * [x] Ensure all Models inherit correctly from `BaseModel`.
> * [x] Resolve circular dependencies in `src/models/__init__.py`.
> * [ ] Generate Alembic Migrations.

---

### **Day 2: Abstract Logic & Polymorphism**

**Goal:** Implement Business Logic using Classes and Interfaces (Mocking the DB).

#### **Dev 1 : Auth Service**

* **Scope:** `src/services/auth_service.py`
  * [x] **(Red)** Create `tests/unit/test_auth_service.py`. Mock `UserRepository`.
  * [x] **(Green)** Implement `AuthService` class.
    * **DI:** `__init__(self, user_repo: AbstractRepository)`.
    * **Method:** `login(username, password) -> Token`.

#### **Dev 2: Repository Pattern**

* **Scope:** `src/repositories/`
  * [x] **(Red)** Create `tests/unit/test_base_repo.py`.
  * [x] **(Green)** Create `src/repositories/base.py`: Define `AbstractRepository` (ABC) and `SqlAlchemyRepository` (Generic Implementation).
  * [x] **(Green)** Create `UserRepository` and `StudentRepository` classes inheriting from `SqlAlchemyRepository`.

#### **Dev 3: Parser Strategy**

* **Scope:** `src/utils/parsers.py`
  * [x] **(Red)** Create `tests/unit/test_parsers.py`.
  * [x] **(Green)** Define `AbstractParser` (ABC) with method `parse(file_stream)`.
  * [x] **(Green)** Implement `UserCSVParser` and `GradeCSVParser` classes (Polymorphism).

#### **Dev 4: Survey Domain Service**

* **Scope:** `src/services/survey_service.py`
  * [x] **(Red)** Create `tests/unit/test_survey_service.py`. Mock `StudentRepository`.
  * [x] **(Green)** Implement `SurveyService` class.
    * **DI:** `__init__(self, survey_repo, student_repo)`.
    * **Method:** `process_skip(student_id)`: Encapsulates the logic of calling `student.increment_misses()`.

#### **Dev 5: Risk Engine (Encapsulation)**

* **Scope:** `src/services/risk_engine.py`
  * [x] **(Red)** Create `tests/unit/test_risk_engine.py`.
  * [x] **(Green)** Implement `RiskCalculator` class.
    * **OOP:** Make weights constants/class attributes.
    * **Method:** `compute(metrics: StudentMetricsDTO) -> float`.

#### **Dev 6: View Objects (Templates)**

* **Scope:** `src/templates/`
  * [x] **(Green)** Create Jinja2 templates (View layer).
  * [x] **(Green)** Ensure templates expect Objects (e.g., `{{ student.risk_score }}`) not Dictionaries.

**🌙 Nightly Refactor (Dev 1):**

> * **Refactor:** Ensure no global functions exist; everything must be a method of a Class.
> * **Refactor:** Verify Dependency Injection signatures in `__init__` methods.

---

### **Day 3: Service Orchestration (Wiring)**

**Goal:** Connect Services to Repositories and expose via Controllers (Blueprints).

#### **Dev 1 : Dependency Injection Container**

* **Scope:** `src/container.py`, `src/app.py`
  * [x] **(Red)** Create `tests/unit/test_container.py`.
  * [x] **(Green)** Implement a simple Container class or factory that instantiates Repos and injects them into Services.
  * [x] **(Green)** Register Blueprints.

#### **Dev 2: Import Orchestrator**

* **Scope:** `src/services/import_service.py`
  * [x] **(Red)** Create `tests/integration/test_import_service.py`.
  * [x] **(Green)** Implement `ImportService` class.
    * **DI:** Inject `UserCSVParser` (the strategy) and `UserRepository`.
    * **Method:** `execute_import(file)`.

#### **Dev 3: Admin Controller**

* **Scope:** `src/api/admin.py`
  * [x] **(Red)** Create `tests/integration/test_admin_routes.py`.
  * [x] **(Green)** Implement Class-based Views (or standard Routes) that call `ImportService.execute_import()`.

#### **Dev 4: Survey Controller**

* **Scope:** `src/api/surveys.py`
  * [x] **(Red)** Create `tests/integration/test_survey_routes.py`.
  * [x] **(Green)** Implement Routes calling `SurveyService.submit()` and `SurveyService.process_skip()`.

#### **Dev 5: Analytics Service (Composition)**

* **Scope:** `src/services/analytics_service.py`
  * [x] **(Red)** Create `tests/integration/test_analytics_service.py`.
  * [x] **(Green)** Implement `AnalyticsService` class.
    * **DI:** Inject `RiskCalculator`, `Anonymizer`, and `StudentRepository`.
    * **Method:** `get_director_view(course_id)`: Orchestrates data fetch $\to$ anonymization $\to$ risk calc.

#### **Dev 6: Analytics Controller**

* **Scope:** `src/api/analytics.py`
  * [x] **(Red)** Create `tests/integration/test_analytics_routes.py`.
  * [x] **(Green)** Implement Routes calling `AnalyticsService`.

**🌙 Nightly Refactor (Dev 1):**

> * **Strict OOP Check:** Ensure Controllers/Routes contain *zero* business logic. They should only parse request $\to$ call Service $\to$ return response.
> * Verify Mocking in tests matches the actual Class Interfaces.

---

### **Day 4: Integration & Interfaces**

**Goal:** Verify Object interactions and handle edge cases.

#### **Dev 1 : E2E Tests**

* **Scope:** `tests/e2e/`
  * [x] **(Red)** Create `TestFullLifecycle` class.
  * [x] **(Green)** Implement flow: Import $\to$ Login $\to$ Survey $\to$ Check Analytics.

#### **Dev 2: Admin Service Extension (Hard Delete)**

* **Scope:** `src/services/admin_service.py`
  * [ ] **(Red)** Create `tests/system/test_cascade.py`.
  * [ ] **(Green)** Add `hard_delete_user(user_id)` to `AdminService`. rely on `UserRepository.delete()`.

#### **Dev 3: Validation Decorators**

* **Scope:** `src/api/validation.py`
  * [x] **(Red)** Create `tests/unit/test_validators.py`.
  * [x] **(Green)** Implement `Validator` class with static methods or Decorators for input validation.

#### **Dev 4: Student Detail Aggregation**

* **Scope:** `src/services/analytics_service.py` (Enhancement)
  * [x] **(Red)** Create `tests/unit/test_history_agg.py`.
  * [x] **(Green)** Add method `get_student_history(id)` to `AnalyticsService`. Returns a `StudentHistoryDTO` object (Data Transfer Object).

#### **Dev 5: DTOs (Data Transfer Objects)**

* **Scope:** `src/dtos/`
  * [x] **(Green)** Define `StudentMetricsDTO`, `RiskReportDTO`.
  * [x] **(Refactor)** Update Services to return DTOs instead of raw Dictionaries (Type Safety).

#### **Dev 6: UI Integration**

* **Scope:** `src/static/js`
  * [ ] **(Green)** Connect HTML forms to API endpoints.

**🌙 Final Refactor (Dev 1):**

> * Review all Classes for Single Responsibility Principle (SRP).
> * Ensure strict Type Hinting is applied (`def method(self, user: User) -> None:`).
> * Final Test Pass.
