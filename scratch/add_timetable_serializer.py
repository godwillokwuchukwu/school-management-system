import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\academics\serializers.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from .models import Class, Enrollment, Grade, Subject",
    "from .models import Class, Enrollment, Grade, Subject, ClassSchedule",
)

new_serializer = """
class ClassScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class_name = serializers.CharField(source="school_class.name", read_only=True)
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = ClassSchedule
        fields = ["id", "school_class", "class_name", "subject", "subject_name", "day_of_week", "day_name", "start_time", "end_time", "room"]
"""
content += new_serializer

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
