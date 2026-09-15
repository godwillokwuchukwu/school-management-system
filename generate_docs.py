import os
import json

docs_dir = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\docs"
os.makedirs(docs_dir, exist_ok=True)

docs = {
    "ARCHITECTURE.md": """# Architecture

## Technology Stack
- **Backend:** Django 6.1.1, DRF 3.18, Celery 5.6
- **Database:** PostgreSQL 17, Redis 8
- **Frontend:** React 19, Vite (Note: Frontend repo separate)

## System Architecture Diagram
```mermaid
flowchart TD
    Client --> API[Django REST Framework]
    API --> DB[(PostgreSQL)]
    API --> Redis[(Redis)]
    API --> Celery[Celery Workers]
    Celery --> DB
    Celery --> Redis
```

## Module Overview
- **Core:** School model and tenant base.
- **Accounts:** Roles, Profiles, JWT auth, AuditLog.
- **Academics:** Subjects, Classes.
- **Students:** Demographics, medical, relations.
- **Admissions:** Application workflow.
- **Attendance:** Daily marking.
- **Activities:** Assignments, events.
- **Communications:** Internal messaging.
- **Fees:** Invoicing, payments.
- **Reporting:** Generated reports.
- **Warehouse:** ETL & analytics.
- **AI Assistants:** Chatbot integrations.
- **Public Site:** External CMS.

## Authentication & JWT Lifecycle
Users login to receive access (1h) and refresh (24h) tokens. The JWT payload includes the `role` to dictate DRF permissions. Tokens are refreshed via standard SimpleJWT endpoints.
""",
    "DATA_DICTIONARY.md": """# Data Dictionary

## Core Entities
- **User:** Django auth user.
- **Profile:** Extends user with `role` (Admin, Teacher, Student, Parent, Applicant).

## KPIs
- **Attendance Rate:** % of days present.
- **Grade Average:** Cumulative GPA.
- **Fee Collection Rate:** Paid vs Invoiced amount.
- **Enrollment Counts:** Active students per term.

## Data Lineage
```mermaid
flowchart LR
    OpDB[(Operational DB)] --> ETL[Nightly ETL]
    ETL --> Fact[(Fact Tables)]
    ETL --> Dim[(Dimension Tables)]
    Fact --> Analytics[Warehouse Analytics]
```
""",
    "ML_DOCUMENTATION.md": """# ML Documentation

## Model Cards
- **Low Attendance Detection:** Identifies students at risk based on absence streaks.
- **Outstanding Fees:** Predicts likelihood of delayed payments.

## ETL Pipeline
The pipeline runs via a Celery beat schedule (`run_etl_pipeline` nightly) to load Dimensions and Facts into the warehouse schemas.

## Evaluation & Monitoring
Monitored via `DataQualityScore` metrics on completeness, freshness, and accuracy.
""",
    "AI_DOCUMENTATION.md": """# AI Assistants Documentation

## Features
Four main roles are implemented via standard APIs using the `call_gemini_api` stub:
1. **Chatbot** - General queries.
2. **Teacher** - Grading assistance, lesson plans.
3. **Admin** - Reporting insights.
4. **Explainer** - Tutoring for students.

## Architecture & Guardrails
- Roles are strictly enforced at the endpoint level (`accounts.permissions`).
- All interactions are logged via `AIAuditLog`.
- Human-in-the-loop for final grade assignments or sensitive communications.
""",
    "USER_GUIDE_ADMIN.md": """# Admin User Guide

## Dashboard
Provides system-wide KPIs: enrollment, collections, attendance.

## Account Management
- **Provisioning:** Create invites via RegistrationInvitation.
- **Classes/Subjects:** Setup via the Academics module.
- **Fees:** Generate bulk invoices.
""",
    "USER_GUIDE_TEACHER.md": """# Teacher User Guide

## Class Management
- View assigned classes and students.
- **Attendance:** Bulk marking interface for daily rolls.
- **Assignments:** Create and grade student submissions.
""",
    "USER_GUIDE_PARENT.md": """# Parent User Guide

## Monitoring
- Track children's attendance and assignment grades.
- Pay and track fee invoices.
- Message teachers directly.
""",
    "USER_GUIDE_STUDENT.md": """# Student User Guide

## Dashboard
- View daily schedule, announcements, and upcoming assignments.
- Submit work.
- Check grades and message teachers.
""",
    "API_REFERENCE.md": """# API Reference

## Authentication
```bash
curl -X POST /api/token/ -d '{"username": "admin", "password": "password"}' -H "Content-Type: application/json"
```

## Accounts
- `GET /api/accounts/profile/` - Fetch current profile.

## Academics
- `GET /api/academics/subjects/` - List subjects.

*(Full endpoint specifications are generated via drf-spectacular at /api/schema/)*
""",
    "FUTURE_ROADMAP.md": """# Future Roadmap

## Out of Scope but Planned
- **Library Management:** Cataloging books, checkouts (would extend core resources).
- **Staff HR & Payroll:** Extend Profile for salary, leave tracking.
- **Hostel & Transport:** Routes, room allocations.
- **Real-time Notifications:** WebSockets/FCM integration.
- **Exam Weighting & GPA:** Complex calculation engine.
- **Automated Report Cards:** PDF generation via Celery.
- **Payment Gateways:** Stripe/Paystack webhook integrations.
""",
}

for filename, content in docs.items():
    with open(os.path.join(docs_dir, filename), "w") as f:
        f.write(content)

print("Documentation generated.")
