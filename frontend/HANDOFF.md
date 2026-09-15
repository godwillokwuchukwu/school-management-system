# Schoolhub frontend handoff

## Prototype scope

The current prototype is a role-aware workspace backed by the Django API. It includes:

- Admin: overview, student directory with search, create, and remove flows, academic overview, attendance register, assignments, messaging, and reporting.
- Teacher: teaching overview, classes and subjects, attendance register, assignment tracker, messaging, and reporting.
- Student: personal academics, attendance, assignments, messages, and reports.
- Parent: the student-facing learning and communication views, ready to be connected to a child selector when the parent-child API is available.

Teacher registration now captures a teaching position and multiple subjects. Teachers can create assignments only for subjects assigned to their profile, message any student through the staff recipient list, and reply to existing student or admin conversations.

All workspace pages use the shared Schoolhub design system. The sidebar becomes an off-canvas menu below 760px, and tables remain horizontally scrollable on small screens.

## API dependencies

The dashboard aggregates `/accounts/profiles/me/`, `/academics/classes/`, `/academics/enrollments/`, `/academics/subjects/`, `/academics/grades/`, `/attendance/records/`, `/activities/assignments/`, `/activities/submissions/`, `/communications/messages/inbox/`, and `/reporting/reports/`. Staff views also hydrate `/students/students/`.

Student creation uses the existing `POST /students/students/` contract. Destructive removal calls `DELETE /students/students/:id/` after browser confirmation.

Teacher setup uses `teaching_position` and `subject_ids` on registration. Parent registration continues to use `child_emails`. The protected `/students/students/recipients/` endpoint exposes only minimal recipient data for staff messaging.

## Known extension points

- Add a parent child selector and parent-specific API aggregation once the relationship endpoint is exposed.
- Connect teacher assignment and attendance actions to the existing write endpoints.
- Add pagination and server-side search for large student directories.
- Replace empty states with chart data once reporting aggregates are available.

## Verification

Run from `frontend/`:

```text
npm run lint
npm run build
```
