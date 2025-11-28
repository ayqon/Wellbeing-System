# **Software Requirements Specification (SRS)**

**Project:** Student Wellbeing Analytics & Tracking System (SWATS)  
**Version:** 0.01 (Prototype / Walking Skeleton)  
**Goal:** To validate the Core Data Ingestion, Privacy Architecture, and Risk Logic.

---

## **1. Introduction**

This prototype serves as a foundational "Walking Skeleton" for the SWATS platform. It focuses on proving the **Dual-Privacy Architecture** (separating Identity from Analytics for academic staff) and the **Algorithmic Risk Engine**. It excludes complex user management (e.g., Role Context Switching) in favor of a streamlined functional pipeline.

## **2. User Roles**

| Actor | Access Level | Responsibilities |
| :--- | :--- | :--- |
| **Student** | Basic | Log in, Submit Wellbeing Surveys, Skip Surveys (with penalty). |
| **Officer** | **Super Admin** | Import Users/Data (CSV), Hard Delete Users, View **Unanonymized** Risk Data & Historical Trends. |
| **Director** | Restricted | View **Anonymized** Risk & Academic Analytics (Hash-masked IDs) for their course. |

---

## **3. Functional Requirements**

### **3.1 Authentication**

* **FR-AUTH-01:** Simple Username/Password login returning a JWT.
* **FR-AUTH-02:** No complex password rules or context switching for V0.01. One user = One role.

### **3.2 User Administration (Officer Only)**

* **FR-ADM-01 (User Import):** The system shall parse a CSV file containing `username`, `first_name`, `last_name`, `email`, `role`, and `course_code`.
  * **Logic:** Creates a `User` record. If the role is STUDENT, it automatically creates a linked `Student` record and associates it with the specified `Course`.
  * **Default Password:** Sets password to the username reversed (e.g., `alice` $\rightarrow$ `ecila`).
* **FR-ADM-02 (Hard Delete):** The system shall allow the Officer to permanently delete a user by ID.
  * **Cascade:** This must trigger a database cascade, physically removing the `User` record and all dependent data (`Student`, `Survey`, `Enrollments`, `Grades`) to ensure no orphan records remain.

### **3.3 Academic Data Injection (Officer Only)**

* **FR-DATA-01 (Enrollment Import):** CSV upload to link `student_id` $\leftrightarrow$ `module_code` in the `student_modules` table.
* **FR-DATA-02 (Academic Import):** CSV upload for Grades and Attendance.
  * **Grades:** Updates `module_grades` (`final_grade`).
  * **Attendance:** Inserts into `attendance_registers` with status `PRESENT` or `ABSENT` and source `CSV`.

### **3.4 Wellbeing Surveys (Student Only)**

* **FR-SURV-01 (Submission):** Student submits `Stress` (1-5) and `Sleep` (0-24). System records this in `wellbeing_surveys` with status `COMPLETED`.
* **FR-SURV-02 (Skip Logic):** Student can explicitly "Skip" a survey.
  * **Logic:** Creates a `wellbeing_surveys` record with status `SKIPPED`.
  * **Penalty:** Immediately increments `students.consecutive_misses` by 1, which increases the calculated Risk Score.

### **3.5 Algorithmic Risk Engine**

* **FR-RISK-01:** The system shall calculate risk dynamically upon API request using the following weighted formula:
    $$RiskScore = \frac{(Stress \times 20) + (100 - Sleep \times 8) + (Misses \times 10) + (100 - Grade)}{4}$$
  * *Note:* `Stress` is normalized to 100 (5*20). `Sleep` reduces risk (inverted). `Misses` add risk. `Grade` reduces risk (inverted).

### **3.6 Analytics & Privacy**

* **FR-VIS-01 (Director View - Anonymized):**
  * **Scope:** Returns only students in the Director's assigned Course.
  * **Privacy:** `Name` and `Student ID` are replaced with a cryptographic **Hash** (e.g., `Student_A9F`).
  * **Data:** Current Risk Score, Average Grade, and Attendance %.
* **FR-VIS-02 (Officer View - Snapshot):**
  * **Privacy:** **Unanonymized** (Real Names shown).
  * **Data:** Table of all students showing Current Risk, latest Stress, latest Sleep, and Total Misses.
* **FR-VIS-03 (Officer View - Trends):**
  * The system shall provide a detailed history view for a specific student, displaying:
    * **Wellbeing Trend:** Line chart of Stress and Sleep over time (Week/Year).
    * **Attendance Trend:** History of Present/Absent status.
    * **Grade History:** List of final grades per module.

---

## **4. Database Schema**

*(Strictly adhering to the corrected definition provided).*

* **`system_config`** (PK: `config_key`, JSONB: `config_value`)
* **`users`** (PK: `user_id`, String: `username`, String: `password_hash`, JSONB: `roles`, Bool: `is_active`, String: `first_name`, String: `last_name`)
* **`students`** (PK: `student_id` [FK $\rightarrow$ Users], FK: `course_code`, Float: `current_risk_score`, Int: `consecutive_misses`)
* **`courses`** (PK: `course_code`, String: `name`, FK: `director_user_id`)
* **`modules`** (PK: `module_code`, FK: `course_code`, FK: `leader_user_id`)
* **`student_modules`** (PK: `student_id`, PK: `module_code`)
* **`module_blocks`** (PK: `block_id`, FK: `module_code`, Date: `start_date`, Date: `end_date`)
* **`wellbeing_surveys`** (PK: `survey_id`, FK: `student_id`, Int: `week`, Int: `year`, Enum: `status`, Int: `stress`, Int: `sleep`)
* **`attendance_registers`** (PK: `register_id`, FK: `student_id`, FK: `module_code`, Date: `session_date`, Enum: `status`, Enum: `source`)
* **`module_grades`** (PK: `grade_id`, FK: `student_id`, FK: `module_code`, Float: `final_grade`)

---

## **5. API Specification (Route Summary)**

### **Authentication**

* `POST /api/auth/login` $\rightarrow$ Returns Session JWT.

### **Admin (Officer)**

* `POST /api/import/users` $\rightarrow$ Bulk create Users + Students (CSV).
* `POST /api/import/enrollments` $\rightarrow$ Bulk link Students to Modules (CSV).
* `POST /api/import/academic` $\rightarrow$ Bulk import Grades/Attendance (CSV).
* `DELETE /api/users/{user_id}` $\rightarrow$ **Hard Delete** User + Cascade Data.

### **Student Actions**

* `POST /api/surveys/submit` $\rightarrow$ Log data (`stress`, `sleep`).
* `POST /api/surveys/skip` $\rightarrow$ Log skip, Increment `misses`.

### **Analytics**

* `GET /api/analytics/director` $\rightarrow$ Returns **Hashed** List `{hash_id, risk, avg_grade, attendance_pct}`.
* `GET /api/analytics/officer/snapshot` $\rightarrow$ Returns **Real Name** List `{id, name, risk, stress, sleep, misses}`.
* `GET /api/analytics/officer/student/{student_id}` $\rightarrow$ Returns **History Details** `{wellbeing_history: [], attendance_history: [], grades: []}`.
