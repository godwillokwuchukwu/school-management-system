import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix throttle rates and pagination
fix = """
import sys
TESTING = len(sys.argv) > 1 and sys.argv[1] in ['test', 'pytest'] or 'pytest' in sys.modules

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100000/day' if TESTING else '100/day',
        'user': '100000/day' if TESTING else '1000/day',
        'auth': '100000/minute' if TESTING else '5/minute', 
        'public_write': '100000/hour' if TESTING else '10/hour', 
        'register': '100000/hour' if TESTING else '10/hour',
        'admin_sensitive': '100000/day' if TESTING else '100/day',
    }
}
"""

content = re.sub(
    r"import sys\nTESTING.*?REST_FRAMEWORK\s*=\s*\{[\s\S]*?\}",
    fix,
    content,
    flags=re.DOTALL,
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
