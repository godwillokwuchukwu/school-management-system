# API Reference

## Authentication
```bash
curl -X POST /api/token/ -d '{"username": "admin", "password": "password"}' -H "Content-Type: application/json"
```

## Accounts
- `GET /api/accounts/profile/` - Fetch current profile.

## Academics
- `GET /api/academics/subjects/` - List subjects.

*(Full endpoint specifications are generated via drf-spectacular at /api/schema/)*
