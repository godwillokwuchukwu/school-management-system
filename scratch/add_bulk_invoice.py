import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\fees\views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

from_block = "from rest_framework.decorators import action"
if from_block not in content:
    content = content.replace(
        "from rest_framework import viewsets, status",
        "from rest_framework import viewsets, status\nfrom rest_framework.decorators import action",
    )

content = content.replace(
    "from .models import Fee, Payment",
    "from .models import Fee, Payment, FeeSchedule\nfrom academics.models import Enrollment",
)

new_action = """
    @action(detail=False, methods=["post"], permission_classes=[IsAdmin])
    def bulk_generate(self, request):
        schedule_id = request.data.get("schedule_id")
        class_id = request.data.get("class_id")
        
        if not schedule_id or not class_id:
            return Response({"detail": "schedule_id and class_id are required."}, status=400)
            
        try:
            schedule = FeeSchedule.objects.get(id=schedule_id)
        except FeeSchedule.DoesNotExist:
            return Response({"detail": "FeeSchedule not found."}, status=404)
            
        enrollments = Enrollment.objects.filter(school_class_id=class_id)
        if not enrollments.exists():
            return Response({"detail": "No enrollments found for this class."}, status=400)
            
        generated = 0
        for enrollment in enrollments:
            # Prevent duplicate fee for the same schedule and student
            fee, created = Fee.objects.get_or_create(
                student=enrollment.student,
                title=f"{schedule.title} ({schedule.academic_year})",
                defaults={
                    "amount": schedule.amount,
                    "due_date": schedule.due_date,
                    "created_by": request.user,
                }
            )
            if created:
                generated += 1
                
        return Response({"detail": f"Successfully generated {generated} invoices."})
"""

content = content.replace(
    "def perform_create(self, serializer):\n        serializer.save(created_by=self.request.user)\n",
    "def perform_create(self, serializer):\n        serializer.save(created_by=self.request.user)\n"
    + new_action,
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
