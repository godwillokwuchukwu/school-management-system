# Stage 13: Architecture Readiness Notes

> **Purpose:** Confirm that Stages 1–12 impose no architectural blockers to any planned extension.  
> **Date:** September 2026  
> **Verdict:** ✅ **No blockers identified.** All extensions can proceed as additive work.

---

## Methodology

Every model, view, URL pattern, middleware, and configuration file across the 13 installed apps was audited against the 5 extension categories defined in Stage 13. For each extension, we verified:

1. Can it be implemented as a **new app** without modifying existing models?
2. If it requires changes to existing models, are those changes **additive** (new fields/FKs) rather than breaking?
3. Does the current **infrastructure** (Redis, Celery, PostgreSQL) support the extension's requirements?
4. Do the current **permissions and authentication** patterns accommodate the extension?

---

## Extension-by-Extension Architecture Assessment

### 13.1 Mobile Applications — ✅ No Blockers

| Aspect | Current State | Extension Requirement | Compatible? |
|--------|--------------|----------------------|-------------|
| API Design | Full REST API under `/api/` with JSON responses | Mobile clients consume REST | ✅ Yes |
| Authentication | JWT via SimpleJWT with `role` + `email` in payload | Token-based mobile auth | ✅ Yes |
| Authorization | Server-side role checks (`IsAdmin`, `IsTeacher`, etc.) | Same permission model | ✅ Yes |
| File Upload | `multipart/form-data` on documents, admissions, careers | Mobile file pickers | ✅ Yes |
| API Spec | OpenAPI 3.0 at `/api/schema/` | Auto-generate mobile SDK | ✅ Yes |
| Pagination | `PageNumberPagination` (100 per page) | Mobile infinite scroll | ✅ Yes, configurable |
| Rate Limiting | Per-class throttling (anon, user, auth, etc.) | Mobile traffic patterns | ⚠️ May need tuning |

**Recommendation:** Add API versioning (`/api/v1/`) before mobile launch to prevent breaking changes.

---

### 13.2 Real-Time Features — ⚠️ Minor Infrastructure Addition

| Aspect | Current State | Extension Requirement | Compatible? |
|--------|--------------|----------------------|-------------|
| Message Broker | Redis 8 at `redis://localhost:6379/1` | Channel layer backend | ✅ Yes (use DB index 3) |
| Async Tasks | Celery 5.6 with Redis broker | Notification delivery | ✅ Yes |
| Chat Models | `Conversation`, `Message`, `MessageReadReceipt` | WebSocket chat | ✅ Yes |
| Server | WSGI (gunicorn) | ASGI (daphne/uvicorn) | ⚠️ Need to add |
| WebSocket Library | Not installed | `channels` + `channels-redis` | ⚠️ Need to add |
| Notification Model | Does not exist | `Notification(user, type, ...)` | ⚠️ New model needed |

**Key Point:** Adding Django Channels is purely additive. The existing WSGI deployment continues to work — Channels adds an ASGI layer alongside it. No existing code needs to change.

```python
# Required additions to requirements.txt:
# channels>=4.0
# channels-redis>=4.0
# daphne>=4.0  (or uvicorn)

# Required additions to INSTALLED_APPS:
# "daphne",  # Must be BEFORE django.contrib.staticfiles
# "channels",
```

---

### 13.3 Physical/Operational Extensions — ✅ All New Apps

Every physical extension (Library, Transport, Hostel, Inventory, Payroll) is implemented as a **new Django app** with its own models, views, serializers, and URLs. None require modifications to existing Stages 1–12 code beyond optional FK relationships.

| Extension | New App | Touches Existing Models? | Infrastructure Needs |
|-----------|---------|------------------------|---------------------|
| QR Attendance | None (uses existing) | No — calls `bulk_mark` API | QR code generator library |
| Digital ID Cards | None (extends existing) | No — reads `Profile.photo` + `Student.admission_number` | Image rendering library |
| Library | `library` | Adds FK to `Student` | None |
| Transport | `transport` | Adds FK to `Student` | GPS tracking service (optional) |
| Hostel | `hostel` | Adds FK to `Student` | None |
| Inventory | `inventory` | None | None |
| Payroll | `hr` | Adds FK to `Profile` | Payment gateway |

**FK additions are non-breaking:** Adding a `ForeignKey` from a new model to `Student` or `Profile` does not modify the existing table — it creates a column in the new model's table.

---

### 13.4 Advanced Optimization & Personalization — ✅ No Blockers

| Feature | Data Source | Current State | Extension Needs |
|---------|-----------|---------------|----------------|
| Timetable Optimization | `ClassSchedule` | Model exists with `day_of_week`, `start_time`, `end_time`, `room` | Constraint solver (OR-Tools, PuLP) |
| Transport Route Optimization | (New) `transport.Route` | Not yet built | Depends on 13.3.4 first |
| Personalized Learning | `FactAcademicPerformance`, `Grade` | Warehouse fact table populated nightly | ML model training pipeline |
| Enrollment Forecasting | `Enrollment`, `DimDate` | Historical enrollment data available | Time-series model (Prophet/ARIMA) |

**The warehouse ETL pipeline** (`warehouse.tasks.run_etl_pipeline`) establishes the pattern for feature engineering. New analytics models follow the same `Dim*/Fact*` pattern.

---

### 13.5 Multi-School / Multi-Tenant SaaS — ✅ Scaffolding in Place

**What's already built:**

```
core.School
├── name (CharField, unique)
├── slug (SlugField, unique)          ← URL-safe identifier for routing
├── domain (CharField)                ← Reserved for subdomain routing
├── is_default (BooleanField)         ← Single-school mode fallback
├── is_active (BooleanField)          ← Soft disable for schools
└── get_default() classmethod         ← Auto-creates default school

accounts.Profile
├── school (FK → core.School)         ← Multi-tenancy anchor
└── save() override                   ← Auto-assigns School.get_default()
```

**What's needed to activate:**

1. **Tenant Middleware** — Extract school from `request.META['HTTP_HOST']` subdomain, attach to `request.school`:
   ```python
   class TenantMiddleware:
       def __call__(self, request):
           host = request.get_host().split(':')[0]
           subdomain = host.split('.')[0]
           request.school = School.objects.get(slug=subdomain)
           return self.get_response(request)
   ```

2. **Scoped QuerySet Manager** — Base manager that auto-filters by `request.school`:
   ```python
   class TenantManager(models.Manager):
       def for_school(self, school):
           return self.filter(school=school)
   ```

3. **Add `school` FK to 14 models** — Additive migration, no data loss:
   - `academics.Subject`, `academics.Class`
   - `attendance.AttendanceRecord`
   - `activities.Assignment`, `activities.Event`, `activities.ParentTeacherMeeting`
   - `communications.Announcement`, `communications.Conversation`
   - `fees.Fee`, `fees.FeeSchedule`
   - `reporting.Report`
   - `admissions.AdmissionApplication`
   - `public_site.SchoolProfile`, `public_site.NewsArticle`, etc.

4. **Cross-tenant isolation test suite** — Verify no data leaks between schools.

**Confirmed:** The `school_id` column on `Profile` means every user is already associated with a school. The migration path is to add the same FK to remaining models and scope querysets.

---

## Infrastructure Readiness Summary

| Component | Current State | Extension-Ready? |
|-----------|--------------|-------------------|
| **Database** | PostgreSQL 17 (SQLite local dev) | ✅ Supports all extensions |
| **Cache/Broker** | Redis 8 (Celery broker + results) | ✅ Can add Channels layer |
| **Task Queue** | Celery 5.6 with Beat scheduler | ✅ Notification delivery, ML pipelines |
| **File Storage** | Local `MEDIA_ROOT` | ⚠️ Should migrate to S3/GCS for production |
| **CI/CD** | GitHub Actions with 85% coverage gate | ✅ Extensible to mobile builds |
| **Containerization** | Docker + docker-compose | ✅ Add new services as needed |
| **API Documentation** | drf-spectacular (Swagger + ReDoc) | ✅ Auto-discovers new viewsets |
| **Authentication** | SimpleJWT (access + refresh) | ✅ Works for mobile, WebSocket auth |

---

## Final Verdict

> [!NOTE]
> **Stages 1–12 impose zero architectural blockers on any planned extension.** The API-first design, role-based permissions, school FK scaffolding, Redis infrastructure, and warehouse ETL pattern collectively ensure that every extension in Stage 13 can be implemented as additive work without breaking changes to the existing system.

The single recommendation before starting any extension: ensure the core platform has been **running stably in production for at least one full school term** so that extension priorities are driven by real usage data rather than speculation.

