import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\accounts\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "class LoginView(TokenObtainPairView):",
    'from rest_framework.throttling import ScopedRateThrottle\n\nclass LoginView(TokenObtainPairView):\n    throttle_classes = [ScopedRateThrottle]\n    throttle_scope = "auth"',
)
content = content.replace(
    "class PasswordResetRequestView(APIView):",
    'class PasswordResetRequestView(APIView):\n    throttle_classes = [ScopedRateThrottle]\n    throttle_scope = "auth"',
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
