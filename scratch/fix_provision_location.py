import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\admissions\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Extract provision block
match = re.search(
    r'(\s*@action\(detail=True, methods=\["post"\]\)\s*def provision\(self, request, pk=None\):.*?return Response\(\{.*?\}\)\n)',
    content,
    flags=re.DOTALL,
)
if match:
    provision_block = match.group(1)
    content = content.replace(provision_block, "")  # remove from old location

    # Insert into AdmissionApplicationAdminViewSet
    target = "class AdmissionApplicationAdminViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):"
    content = content.replace(target, target + "\n" + provision_block + "\n")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed provision location")
else:
    print("Provision block not found")
