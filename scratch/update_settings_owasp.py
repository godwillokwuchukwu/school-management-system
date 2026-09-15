import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Make security settings robust
security_settings = """
# Stage 10: OWASP Baseline (Enabled in prod/secure contexts)
import os

SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "False").lower() == "true"
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Add REST_FRAMEWORK throttling defaults
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'auth': '5/minute', # strict login/reset throttling
    }
}
"""

content = re.sub(r"REST_FRAMEWORK\s*=\s*\{[\s\S]*?\}", security_settings, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
