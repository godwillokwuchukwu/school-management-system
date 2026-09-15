import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\accounts\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """        if User.objects.filter(email=email).exists():
            return Response({"detail": "User already exists."}, status=400)

        invitation = RegistrationInvitation.objects.create("""

new_block = """        if User.objects.filter(email=email).exists():
            return Response({"detail": "User already exists."}, status=400)
            
        if RegistrationInvitation.objects.filter(email=email).exists():
            return Response({"detail": "An invitation for this email already exists."}, status=400)

        invitation = RegistrationInvitation.objects.create("""

content = content.replace(old_block, new_block)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
