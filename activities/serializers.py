from rest_framework import serializers

from students.models import Student

from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        request = self.context.get("request")
        profile = getattr(getattr(request, "user", None), "profile", None)
        if profile and profile.role == "teacher":
            subject = attrs.get("subject", getattr(self.instance, "subject", None))
            if subject and not profile.teaching_subjects.filter(pk=subject.pk).exists():
                raise serializers.ValidationError(
                    {
                        "subject": "You can only create assignments for subjects assigned to you."
                    }
                )
        return attrs

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "description",
            "subject",
            "school_class",
            "due_date",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        return super().create(validated_data)


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    # Not required at the field level: a submitting student never sends
    # this (the app fills it in from their own profile in create()) --
    # only an admin/teacher creating a submission on a student's behalf
    # needs to supply it, which validate() below still enforces.
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), required=False
    )

    def validate(self, attrs):
        request = self.context.get("request")
        profile = getattr(getattr(request, "user", None), "profile", None)
        student = attrs.get("student")
        if profile and profile.role == "student":
            own_student = getattr(profile, "student", None)
            if student and student != own_student:
                raise serializers.ValidationError(
                    {
                        "student": "You can only submit work for your own student profile."
                    }
                )
            student = attrs["student"] = own_student
        elif not student and not self.instance:
            raise serializers.ValidationError({"student": "This field is required."})

        # DRF's auto unique_together validator (disabled below, via
        # Meta.validators) would otherwise force `student` required at the
        # field level even though it's normally filled in server-side --
        # so the uniqueness check it would have done is done here instead.
        assignment = attrs.get("assignment", getattr(self.instance, "assignment", None))
        if student and assignment:
            conflict = AssignmentSubmission.objects.filter(
                assignment=assignment, student=student
            )
            if self.instance:
                conflict = conflict.exclude(pk=self.instance.pk)
            if conflict.exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "A submission for this assignment already exists for this student."
                        ]
                    }
                )
        return attrs

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "assignment",
            "student",
            "content",
            "status",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = ["submitted_at", "updated_at"]
        validators = []  # replaced by the manual uniqueness check in validate() above

    def create(self, validated_data):
        request = self.context.get("request")
        if (
            request
            and request.user.is_authenticated
            and getattr(request.user, "profile", None)
        ):
            if request.user.profile.role == "student":
                student = getattr(request.user.profile, "student", None)
                if student is not None:
                    validated_data["student"] = student
        return super().create(validated_data)


from .models import Event, ParentTeacherMeeting


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "category",
            "start_time",
            "end_time",
            "location",
            "school_class",
            "is_school_wide",
            "created_at",
            "updated_at",
        ]


class ParentTeacherMeetingSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    parent_name = serializers.CharField(source="parent.get_full_name", read_only=True)
    student_name = serializers.CharField(
        source="student.profile.user.get_full_name", read_only=True
    )

    class Meta:
        model = ParentTeacherMeeting
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "parent",
            "parent_name",
            "student",
            "student_name",
            "start_time",
            "end_time",
            "status",
            "video_url",
            "notes",
            "created_at",
            "updated_at",
        ]
