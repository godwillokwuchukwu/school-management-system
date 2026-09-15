# Schoolhub Design System

## Product direction
Schoolhub is a calm, operational interface for school teams. The visual system uses navy for trust and navigation, emerald for healthy progress, coral for errors, and generous white space for scanning.

## Color tokens

| Token | Value | Usage |
| --- | --- | --- |
| Navy | `#152F4F` | Sidebar, primary navigation |
| Navy strong | `#1E3A5F` | Primary buttons, emphasis |
| Emerald | `#10B981` | Success, attendance, positive trends |
| Coral | `#EC6A68` | Alerts, errors, unread indicators |
| Canvas | `#F6F8FB` | Application background |
| Ink | `#152033` | Headings and primary text |
| Muted | `#738096` | Supporting text |
| Line | `#E6EBF1` | Dividers and input borders |

## Typography

- UI family: Trebuchet MS with Segoe UI fallback.
- Page headings: 27-30px, bold, tight line height.
- Panel headings: 14px, bold.
- Body copy: 12px.
- Labels and metadata: 9-11px.
- Uppercase eyebrows: 10px, 1.4px tracking, bold.

## Spacing and shape

- Base spacing: 4px.
- Common spacing: 8, 12, 16, 20, 24, 40px.
- Cards and panels: 7px radius.
- Inputs: 5px radius.
- Auth card: 10px radius.
- Borders: 1px solid `#E6EBF1`.
- Elevation: `0 4px 14px #17324D08` for panels; `0 25px 80px #06192C55` for auth.

## Components

- `primary-button`: navy action with emerald arrow affordance.
- `nav-item`: sidebar navigation with active emerald inset marker.
- `stat-card`: icon, label, value, trend, and overflow action.
- `panel`: white bordered content surface.
- `tag`: compact status label; use text and color together.
- `auth-card`: shared container for sign in, registration, and reset screens.

## Responsive rules

- Desktop: sidebar + content, 4-column metrics.
- Tablet: 214px sidebar, 2-column metrics.
- Mobile: stacked panels, compact topbar, single-column forms.

## Authentication states

1. Sign in with email and password.
2. Register with name, email, password, phone, and role.
3. Role options: Student, Parent, Teacher, Administrator.
4. Forgot password request and confirmation state.
5. API/network errors are displayed inline and do not silently authenticate.

## Django handoff

- API base: `VITE_API_URL` or `http://localhost:8000/api`.
- Login: `POST /auth/login/` with `username` and `password`.
- Registration: `POST /auth/register/` with `email`, `password`, `first_name`, `last_name`, `role`, and `phone`.
- Access tokens are sent as `Authorization: Bearer <token>`.
- The shared API client refreshes expired access tokens using `/auth/refresh/`.
- Role is read from the JWT and confirmed by `/accounts/profiles/me/`.
