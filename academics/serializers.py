from rest_framework import serializers

from accounts import audit

from .models import Class, Enrollment, Grade, Subject, ClassSchedule


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "code", "description"]


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name", "code", "academic_year", "class_teacher", "subjects"]

    def validate(self, attrs):
        # Mirrors the DB UniqueConstraint with a friendly message instead
        # of surfacing an IntegrityError to the client.
        code = attrs.get("code", getattr(self.instance, "code", None))
        year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        qs = Class.objects.filter(code=code, academic_year=year)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {
                    "code": "A class with this code already exists for this academic year."
                }
            )
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="school_class.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "school_class",
            "class_name",
            "academic_year",
            "enrolled_at",
        ]
        read_only_fields = ["enrolled_at"]

    def validate(self, attrs):
        student = attrs.get("student", getattr(self.instance, "student", None))
        school_class = attrs.get(
            "school_class", getattr(self.instance, "school_class", None)
        )
        year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        qs = Enrollment.objects.filter(
            student=student, school_class=school_class, academic_year=year
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "This student is already enrolled in this class for this year."
            )
        return attrs


class GradeSerializer(serializers.ModelSerializer):
    letter_grade = serializers.CharField(read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Grade
        fields = [
            "id",
            "enrollment",
            "subject",
            "subject_name",
            "score",
            "letter_grade",
            "graded_by",
            "graded_at",
            "updated_at",
        ]
        read_only_fields = ["graded_by", "graded_at", "updated_at"]

    def validate_score(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Score must be between 0 and 100.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["graded_by"] = request.user
        grade = super().create(validated_data)
        audit.record(
            actor=request.user,
            action="grade.create",
            instance=grade,
            new_value={"score": str(grade.score)},
            request=request,
        )
        return grade

    def update(self, instance, validated_data):
        request = self.context["request"]
        old_score = instance.score
        grade = super().update(instance, validated_data)
        if "score" in validated_data and validated_data["score"] != old_score:
            audit.record(
                actor=request.user,
                action="grade.update",
                instance=grade,
                old_value={"score": str(old_score)},
                new_value={"score": str(grade.score)},
                request=request,
            )
        return grade


class ClassScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class_name = serializers.CharField(source="school_class.name", read_only=True)
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = ClassSchedule
        fields = [
            "id",
            "school_class",
            "class_name",
            "subject",
            "subject_name",
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
            "room",
        ]
