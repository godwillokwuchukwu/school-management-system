import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\frontend\src\api.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_methods = """
  activateAccount: (token, password) => request('/accounts/activate/', { method: 'POST', body: JSON.stringify({ token, password }) }),
  adminProvisionAccount: (data) => request('/accounts/admin/provision/', { method: 'POST', body: JSON.stringify(data) }),
  adminSuspendProfile: (id) => request(`/accounts/profiles/${id}/suspend/`, { method: 'POST' }),
  adminReactivateProfile: (id) => request(`/accounts/profiles/${id}/reactivate/`, { method: 'POST' }),
"""

# Insert before deleteStudent
content = content.replace(
    "deleteStudent: (id) => request(`/students/students/${id}/`, { method: 'DELETE' }),",
    new_methods
    + "\n  deleteStudent: (id) => request(`/students/students/${id}/`, { method: 'DELETE' }),",
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
