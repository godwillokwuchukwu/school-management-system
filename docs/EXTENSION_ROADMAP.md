# Stage 13: Extension Roadmap

> **Status:** Planning/Architecture-Preservation Only  
> **Prerequisite:** Stages 1–12 must be live, stable, and running in a real school term before any extension is started.

---

## Prioritization Framework

Extensions are prioritized against three criteria:
1. **User Impact** — How many users benefit and how frequently?
2. **Architecture Readiness** — Does the current codebase already scaffold for this?
3. **Complexity** — How much new infrastructure, models, and UI are required?

| Priority | Extension | Impact | Readiness | Complexity |
|----------|-----------|--------|-----------|------------|
| **P0** | Push Notifications & Real-Time | High | Medium | Medium |
| **P1** | Mobile Applications | High | High | Medium |
| **P1** | QR Attendance | High | High | Low |
| **P2** | Library Management | Medium | Low | Medium |
| **P2** | Timetable Optimization | Medium | Medium | Medium |
| **P2** | Payroll for Staff | Medium | Low | High |
| **P3** | Transport Management | Medium | Low | Medium |
| **P3** | Hostel Management | Low | Low | Medium |
| **P3** | Digital ID Cards | Low | Medium | Low |
| **P3** | Inventory Management | Low | Low | Medium |
| **P4** | Personalized Learning | Medium | Medium | High |
| **P4** | Advanced Forecasting | Medium | Medium | High |
| **P5** | Multi-School SaaS | High | High | Very High |

---

## 13.1 Mobile Applications

### Vision
Native iOS and Android apps (or React Native/Flutter cross-platform) for students, parents, teachers, and administrators — sharing the exact same backend API from Stages 1–9.

### Architecture Readiness: ✅ HIGH
- **API-first design:** Every feature is exposed through RESTful JSON endpoints under `/api/`.
- **JWT authentication:** `SimpleJWT` issues access/refresh tokens with `role` and `email` embedded in the payload — mobile clients decode these identically to the React app.
- **No mobile-specific business logic required:** All permission checks, role scoping, and data filtering happen server-side via DRF permissions (`IsAdmin`, `IsTeacher`, `IsStudent`, `IsParent`, `IsApplicant`).
- **File uploads:** `multipart/form-data` endpoints already exist for documents, admission files, and job resumes.
- **OpenAPI schema:** `/api/schema/` generates a machine-readable spec that can auto-generate mobile API clients.

### Blockers: None
### Prerequisites Before Starting:
- Production API must be stable for ≥1 school term
- Rate limiting tuned for mobile traffic patterns (shorter sessions, more frequent small requests)
- Consider adding API versioning (`/api/v1/`) before mobile launch to avoid breaking changes

---

## 13.2 Real-Time Features

### Vision
Push notifications, WebSocket-based live chat, presence indicators, typing indicators, and real-time attendance dashboard updates.

### Architecture Readiness: ⚠️ MEDIUM
- **Redis already deployed:** `redis://localhost:6379/1` (Celery broker) and `/2` (results). Redis can serve as the Django Channels channel layer on a separate DB index (`/3`).
- **Celery task infrastructure exists:** `communications.tasks.send_email_notification` already handles async email — extending to push notification delivery is straightforward.
- **Conversation/Message models exist:** `communications.Conversation`, `Message`, `MessageReadReceipt` provide the data layer for real-time chat.
- **`AuditLogMiddleware` captures client IP:** Foundation for tracking connection metadata.

### Blockers: Minor
- **Django Channels not installed:** `channels` and `channels-redis` must be added to `requirements.txt` and `INSTALLED_APPS`.
- **ASGI entrypoint needed:** Current deployment uses WSGI (`gunicorn`). Channels requires an ASGI server (`daphne` or `uvicorn`) and an `asgi.py` routing configuration.
- **No notification model:** Need `Notification(user, type, title, body, is_read, created_at)` model and a `NotificationConsumer` WebSocket consumer.

### Implementation Notes:
```
# Future config/asgi.py structure
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/notifications/", NotificationConsumer.as_asgi()),
            path("ws/chat/<conversation_id>/", ChatConsumer.as_asgi()),
        ])
    ),
})
```

---

## 13.3 Physical/Operational Extensions

### 13.3.1 QR Attendance
**Readiness: ✅ HIGH** — `AttendanceRecord(student, date, status, marked_by)` already exists. QR scanning simply calls the existing `bulk_mark` endpoint with a decoded student ID. Requires only a mobile camera integration and QR code generation for student IDs.

### 13.3.2 Digital Student/Teacher ID Cards
**Readiness: ⚠️ MEDIUM** — `Profile.photo` (ImageField) and `Student.admission_number` already exist. Generation requires a card template renderer (e.g., Pillow or WeasyPrint) and a QR code encoding the admission number for verification scanning.

### 13.3.3 Library Management
**Readiness: 🔴 LOW** — No library models exist. Requires new app:
- Models: `Book`, `BookCopy`, `BorrowRecord`, `Fine`
- Views: Catalog search, borrow/return, overdue tracking
- Integration: `Fee` model for fines, `Student` FK for borrowers

### 13.3.4 Transport Management
**Readiness: 🔴 LOW** — No transport models exist. Requires new app:
- Models: `Route`, `Stop`, `Bus`, `Driver`, `StudentRouteAssignment`
- Views: Route planning, student pickup assignments, driver schedules
- Integration: `Student` FK, potentially GPS tracking

### 13.3.5 Hostel Management
**Readiness: 🔴 LOW** — No hostel models exist. Requires new app:
- Models: `Hostel`, `Room`, `BedAssignment`, `HostelAttendance`
- Views: Room allocation, occupancy tracking, hostel-specific attendance
- Integration: `Student` FK, `AttendanceRecord` extension for hostel check-in

### 13.3.6 Inventory Management
**Readiness: 🔴 LOW** — No inventory models exist. Requires new app:
- Models: `Asset`, `AssetCategory`, `AssetAssignment`, `MaintenanceRecord`
- Views: Asset tracking, assignment to rooms/teachers, depreciation

### 13.3.7 Staff Payroll
**Readiness: 🔴 LOW** — While `Profile(role=teacher)` and `teaching_position` exist, there are no payroll models. Requires:
- Models: `SalaryStructure`, `PaySlip`, `Deduction`, `Allowance`, `LeaveRequest`, `LeaveBalance`
- Views: Payroll generation, leave management, tax calculation
- Integration: `Profile` FK, `Fee`/`Payment` patterns for payment processing

---

## 13.4 Advanced Optimization & Personalization

### 13.4.1 Timetable Optimization
**Readiness: ⚠️ MEDIUM** — `ClassSchedule(school_class, subject, day_of_week, start_time, end_time, room)` exists but lacks conflict detection. Optimization would use constraint-satisfaction algorithms to auto-generate schedules avoiding teacher/room/class conflicts.

### 13.4.2 Transport Route Optimization
**Readiness: 🔴 LOW** — Blocked by 13.3.4 (Transport Management). Once routes exist, optimization can apply graph algorithms for efficient pickup ordering.

### 13.4.3 Personalized Learning Recommendations
**Readiness: ⚠️ MEDIUM** — `warehouse.FactAcademicPerformance` and `FactAttendance` provide the feature store. `Grade.letter_grade` and subject-level scores enable topic-specific weakness detection. Requires ML model training on historical performance data.

### 13.4.4 Advanced Forecasting
**Readiness: ⚠️ MEDIUM** — `warehouse.DimDate` provides the temporal dimension. `FactAttendance` and `FactAcademicPerformance` provide historical trends. Enrollment forecasting can leverage `Enrollment` counts by `academic_year`. Requires time-series modeling (Prophet, ARIMA, or similar).

---

## 13.5 Multi-School / Multi-Tenant SaaS

### Vision
Transform the single-school deployment into a multi-tenant SaaS platform where each school gets its own subdomain, branding, data isolation, and configuration.

### Architecture Readiness: ✅ HIGH (Scaffolding in Place)

**Already implemented:**
- `core.School` model with `name`, `slug`, `domain`, `is_default`, `is_active`
- `accounts.Profile.school` FK to `core.School` (auto-assigned via `School.get_default()` on save)
- `School.domain` field reserved for subdomain routing
- Architecture note in `School` docstring explicitly calls out Stage 13.5

**Required for activation:**
1. **Tenant-aware middleware:** Extract school from subdomain/header, attach to `request.school`
2. **Queryset scoping:** Add `.filter(school=request.school)` or use a custom manager across all models
3. **Add `school` FK to remaining models:** Currently only `Profile` has it. Must add to:
   - `academics.Class`, `academics.Subject`
   - `attendance.AttendanceRecord`
   - `activities.Assignment`, `activities.Event`
   - `communications.Announcement`, `communications.Conversation`
   - `fees.Fee`, `fees.FeeSchedule`
   - `reporting.Report`
   - `admissions.AdmissionApplication`
   - `public_site.*` (all public content models)
4. **Tenant-specific settings:** Branding (logo, colors), academic calendar, grading scale, payment gateway credentials
5. **Cross-tenant data isolation tests:** Explicit security suite verifying no data leaks between schools

### Critical Warning:
> [!CAUTION]
> Multi-tenancy is the highest-complexity extension. It touches every model, every queryset, every view, and every test. It should NOT be started until the single-school deployment has been running stably for multiple school terms and the team has experience with the codebase.

---

## Architecture Blockers Assessment

### Confirmed: No Blockers from Stages 1–12

| Extension | Potential Blocker | Assessment |
|-----------|-------------------|------------|
| Mobile Apps | API not REST-ful | ✅ **No blocker.** Full REST API with JWT auth, OpenAPI schema, and role-scoped endpoints. |
| Real-Time | No WebSocket support | ⚠️ **Minor.** Redis deployed, Channels not yet installed. Adding Channels is additive, not breaking. |
| QR Attendance | No barcode/QR model | ✅ **No blocker.** QR simply encodes existing `admission_number`, calls existing `bulk_mark` API. |
| Library | No library models | ✅ **No blocker.** New app, no conflicts with existing models. |
| Transport | No transport models | ✅ **No blocker.** New app, no conflicts. |
| Hostel | No hostel models | ✅ **No blocker.** New app, no conflicts. |
| Payroll | No payroll models | ✅ **No blocker.** New app, Profile FK available. |
| Timetable Opt. | ClassSchedule lacks constraints | ✅ **No blocker.** Constraint validation is additive. |
| Personalization | No ML pipeline | ✅ **No blocker.** Warehouse fact tables provide feature store. |
| Multi-Tenant | `school` FK missing on most models | ✅ **No blocker.** `Profile.school` FK exists as anchor. Migration to add FK to other models is straightforward. |

### Key Architecture Decisions That Enable Extensions

1. **API-first design** — Every feature is a REST endpoint, making mobile/third-party integration trivial.
2. **Role-based permissions** — `IsAdmin`, `IsTeacher`, `IsStudent`, `IsParent`, `IsApplicant` permission classes enforce access at the view level, not the client level.
3. **`school` FK on Profile** — The multi-tenancy anchor is already in the database, auto-populated on every profile creation.
4. **Redis infrastructure** — Already deployed for Celery; ready to serve as Channels layer and cache backend.
5. **Warehouse ETL pattern** — `warehouse.tasks.run_etl_pipeline` provides a template for any future analytics pipeline.
6. **Audit logging** — `AuditLog` and `AIAuditLog` models establish a pattern for compliance-ready extensions.
7. **Document management** — `core.Document` with file validation, malware scanning stub, and category system is extensible to any document-heavy feature.

---

## Extension Development Protocol

> [!IMPORTANT]
> Each extension, when eventually started, **must** follow the same process used for the original build:

1. **Gap Analysis** — Equivalent to Stage 0. Audit the current codebase against the extension requirements.
2. **Staged Plan** — Break the extension into phases with clear deliverables and exit criteria.
3. **Schema Design** — Design models, relationships, and migrations before writing views.
4. **Permission Design** — Define who can access what before writing endpoints.
5. **Test-First** — Write test cases before or alongside implementation. Maintain ≥85% coverage.
6. **Documentation** — Update `docs/` with new models, endpoints, and user guides.
7. **Security Review** — Run the Stage 10 OWASP baseline against new endpoints before deployment.

---

## Timeline Guidance

| Phase | Extensions | Start Condition |
|-------|-----------|-----------------|
| **Phase A** (Term 2) | Push Notifications, QR Attendance | After 1 stable term in production |
| **Phase B** (Term 3) | Mobile Apps (iOS/Android) | After Phase A is stable |
| **Phase C** (Year 2) | Library, Timetable Optimization | After core platform is mature |
| **Phase D** (Year 2+) | Transport, Hostel, Payroll | Based on school operational needs |
| **Phase E** (Year 3+) | Multi-Tenant SaaS | Only after extensive single-school production experience |

> [!NOTE]
> These timelines are guidance, not commitments. Each extension should be triggered by **real usage data and user feedback** from the live platform, not by a predetermined schedule.

