import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Disable throttling during tests
fix = """
import sys
TESTING = len(sys.argv) > 1 and sys.argv[1] in ['test', 'pytest'] or 'pytest' in sys.modules

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [] if TESTING else [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'auth': '5/minute', 
        'public_write': '10/hour', 
    }
}
"""

content = re.sub(r"REST_FRAMEWORK\s*=\s*\{[\s\S]*?\}", fix, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
