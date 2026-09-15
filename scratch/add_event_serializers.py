import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\activities\serializers.py"

new_serializers = """
from .models import Event, ParentTeacherMeeting

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id", "title", "description", "category", "start_time", 
            "end_time", "location", "school_class", "is_school_wide",
            "created_at", "updated_at"
        ]

class ParentTeacherMeetingSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    parent_name = serializers.CharField(source="parent.get_full_name", read_only=True)
    student_name = serializers.CharField(source="student.profile.user.get_full_name", read_only=True)

    class Meta:
        model = ParentTeacherMeeting
        fields = [
            "id", "teacher", "teacher_name", "parent", "parent_name", 
            "student", "student_name", "start_time", "end_time", 
            "status", "video_url", "notes", "created_at", "updated_at"
        ]
"""

with open(file_path, "a", encoding="utf-8") as f:
    f.write(new_serializers)
