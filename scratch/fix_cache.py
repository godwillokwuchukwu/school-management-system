import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix cache
fix = """
import sys
TESTING = 'pytest' in sys.modules

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
} if TESTING else {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
"""

content = re.sub(
    r"import sys\nTESTING.*?CACHES\s*=\s*\{[\s\S]*?\}", fix, content, flags=re.DOTALL
)
if "CACHES" not in content:
    content += "\n" + fix

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
