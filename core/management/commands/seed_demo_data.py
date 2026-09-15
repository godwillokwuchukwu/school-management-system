from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student
from academics.models import Class, Subject
from warehouse.tasks import run_etl_pipeline
from config import settings


class Command(BaseCommand):
    help = "Seeds realistic demo data for development."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("Cannot run in production!"))
            return

        self.stdout.write("Seeding demo data...")

        # 1. Admin
        if not User.objects.filter(email="admin@demo.com").exists():
            u = User.objects.create_superuser(
                "admin@demo.com", "admin@demo.com", "password123"
            )
            u.profile.role = "admin"
            u.profile.save()
            self.stdout.write("Created admin@demo.com")

        # 2. Teacher
        if not User.objects.filter(email="teacher@demo.com").exists():
            u = User.objects.create_user(
                "teacher@demo.com", "teacher@demo.com", "password123"
            )
            u.profile.role = "teacher"
            u.profile.save()
            self.stdout.write("Created teacher@demo.com")

        # 3. Student
        if not User.objects.filter(email="student@demo.com").exists():
            u = User.objects.create_user(
                "student@demo.com", "student@demo.com", "password123"
            )
            u.profile.role = "student"
            u.profile.save()
            self.stdout.write("Created student@demo.com")

            # Create a basic class and subject
            cls = Class.objects.create(
                name="Grade 10A", code="10A", academic_year="2025-2026"
            )
            sub = Subject.objects.create(name="Mathematics", code="MATH101")

            # Attach student profile
            from datetime import date

            Student.objects.create(
                profile=u.profile, dob=date(2010, 1, 1), admission_number="ADM001"
            )
            # Create enrollment
            from academics.models import Enrollment

            student = Student.objects.get(admission_number="ADM001")
            Enrollment.objects.create(
                student=student, school_class=cls, academic_year="2025-2026"
            )
            self.stdout.write("Created demo student profile and class")

        # 4. Trigger ETL to populate warehouse
        run_etl_pipeline()
        self.stdout.write(self.style.SUCCESS("Data warehouse populated."))

        self.stdout.write(self.style.SUCCESS("Demo data seeding complete!"))
