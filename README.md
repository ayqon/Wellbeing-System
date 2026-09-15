# SWATS - Student Wellbeing & Attendance Tracking System
### Collaborative University Software Engineering Initiative | Full-Stack Early Warning & Surveillance Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-emerald.svg)](https://swats-wellbeing-platform.onrender.com/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Framework-Flask%203.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-292%20%2F%20292%20Passed%20(100%25)-emerald.svg)](tests/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20OOP%20%2F%20DI%20Container-purple.svg)](ARCHITECTURE.md)
[![Database](https://img.shields.io/badge/ORM-SQLAlchemy%20%2F%20SQLite-blue.svg)](src/core/database.py)
[![Security](https://img.shields.io/badge/Auth-Bcrypt%20%2B%20JWT%20RBAC-red.svg)](src/services/auth_service.py)

---

## Live Cloud Deployment

* **Live Demo URL**: [https://swats-wellbeing-platform.onrender.com/](https://swats-wellbeing-platform.onrender.com/)
* **Hosted on**: Render Free Tier (Automated CI/CD with Gunicorn & Pre-Seeded SQLite Demo Engine)

---

## Overview

The **Student Wellbeing & Attendance Tracking System (SWATS)** is an early-warning educational surveillance and wellbeing monitoring platform. Developed under strict **Test-Driven Development (TDD)** and **Object-Oriented Design** principles, the platform identifies students facing academic or personal distress through proactive daily wellbeing surveys, attendance metrics, and dynamic risk scoring.

The system incorporates **Privacy by Design**, enforcing SHA-256 hash-masked anonymization for Course Directors while providing unanonymized, multi-variable analytical control to Academic Officers.

---

## Collaborative Team & Architectural Ownership

Developed collaboratively by a 6-engineer agile team with strict separation of domain boundaries and modular interfaces.

| Role | Developer | Module & Core Architectural Ownership |
|:---|:---|:---|
| **DEV 1** | **Muhammad Ibne Muzammil** | Infrastructure, Dependency Injection Container (src/container.py), Dynamic Officer Analytics, Lead TDD Refactoring |
| **DEV 2** | **Ioannis Konstantinou** | **User Domain Model, Authentication Services (src/services/auth_service.py), Token Infrastructure (src/services/token_service.py), RBAC & Security** |
| **DEV 3** | **Mohammad Irfan Mohammad Noor** | Student & Tracking Domain Models, Attendance Logic, Validation Decorator Suite (src/api/validation.py) |
| **DEV 4** | **Wu Zheyu** | Academic Domain Models, High-Throughput CSV Parsing Pipelines (src/utils/parsers.py) |
| **DEV 5** | **Ayan Paul** | Dynamic Risk Engine (src/services/risk_engine.py), Multi-Factor Vulnerability Scoring Algorithms |
| **DEV 6** | **Zhang Zhexian** | Privacy Layer & Data Anonymization Engine (src/utils/privacy.py), Dynamic Analytics Visualization |

---

## Key System Features

### 1. Multi-Tiered Role-Based Access Control (RBAC)
* **Student Dashboard**: Submit daily wellbeing check-ins (sleep hours, stress levels), view personal historical trends, and compare metrics against the cohort average via a **Wellbeing Radar Chart**.
* **Officer Dashboard (Super Admin)**: Complete unanonymized visibility, multi-axis scatter and clustering analytics, hard/soft user deletion, and bulk CSV ingestion.
* **Director Dashboard (Restricted & Anonymized)**: Course-level aggregate performance histograms, grade-vs-attendance correlation charts, and SHA-256 hash-masked student IDs for GDPR compliance.

### 2. Dynamic Risk Scoring Engine
* Real-time calculation of multi-factorial risk scores combining survey responses, chronic non-submission penalties, academic grade dips, and attendance drop-offs.
* Categorizes students into **Low Risk**, **Disengagement Hazard**, **High Stress Hazard**, and **Silent Struggle** cohorts.

### 3. High-Throughput CSV Ingestion Pipeline
* Granular streaming parsers for bulk ingestion of users, academic grades, attendance logs, and survey records with automated rollback on validation failure.

---

## System Architecture

The codebase follows clean layered architectural patterns decoupled via a custom **Dependency Injection Container**:

`	ext
src/
|-- api/            # HTTP Blueprints (Auth, Admin, Analytics, Surveys, Validation)
|-- core/           # Database session & engine configurations
|-- dtos/           # Data Transfer Objects for decoupled service responses
|-- models/         # SQLAlchemy Domain Entities (BaseModel, User, Student, Academic, Survey)
|-- repositories/   # Abstract & Concrete Repository layer (CRUD & domain queries)
|-- services/       # Core business logic (AuthService, RiskEngine, ImportService, Analytics)
|-- static/         # CSS & Chart.js frontend visualization scripts
|-- templates/      # Jinja2 templates for Student, Officer, and Director portals
-- utils/          # Anonymization hashing and CSV stream parsers
`

---

## Quickstart & Local Setup

### 1. Clone & Environment Setup
`ash
git clone https://github.com/ayqon/wellbeing-system.git
cd wellbeing-system

# Install dependencies
pip install -r requirements.txt
`

### 2. Seed Database with Realistic Demo Data
`ash
python -m src.seed
`

### 3. Launch Application
`ash
python -m src.app
`
* Access the platform at: http://127.0.0.1:5000

---

## Demo Credentials

The database seeder automatically initializes realistic accounts across all three user tiers:

| Role | Username | Password | Dashboard Features |
|:---|:---|:---|:---|
| **Student** | student1 | password123 | Daily Survey Form, Personal Wellbeing Radar Chart |
| **Academic Officer** | officer1 | password123 | Full Unanonymized Surveillance, Dynamic Filter Analytics, CSV Import |
| **Course Director** | director1 | password123 | Course Aggregate Histograms, Grade vs Attendance (Hashed IDs) |

---

## Test Suite & Verification

The project enforces comprehensive test coverage across unit, integration, and end-to-end system flows:

`ash
# Execute entire test suite
python -m pytest -v

# Run with test coverage report
python -m pytest --cov=src --cov-report=term-missing
`

* **Test Suite Status**: **292 / 292 tests passing (100% pass rate)**.

---

## Agile Sprint & Engineering Artifacts

Full documentation of system design and sprint refactoring reports:
* [Software Requirements Specification (SRS)](SWATS_v0_01_srs.md)
* [System Architecture & DI Container Design](ARCHITECTURE.md)
* [Sprint Refactor Report - Day 1](REFACTOR_REPORT_DAY_1.md)
* [Sprint Refactor Report - Day 2](REFACTOR_REPORT_DAY_2.md)
* [Sprint Refactor Report - Day 3](REFACTOR_REPORT_DAY_3.md)
