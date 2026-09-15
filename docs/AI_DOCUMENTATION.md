# AI Assistants Documentation

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
