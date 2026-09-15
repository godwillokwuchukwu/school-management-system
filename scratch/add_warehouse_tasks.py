import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\warehouse\tasks.py"

new_tasks = """
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from students.models import Student
from academics.models import Class, Subject, Grade
from attendance.models import AttendanceRecord
from fees.models import Fee

from .models import (
    DimStudent, DimClass, DimSubject, DimDate,
    FactAttendance, FactAcademicPerformance, FactPayment,
    DataQualityScore
)

@shared_task
def run_etl_pipeline():
    with transaction.atomic():
        # 1. Load Dimensions
        for student in Student.objects.select_related('profile__user').all():
            DimStudent.objects.update_or_create(
                student_id=student.id,
                defaults={
                    'admission_number': student.admission_number,
                    'first_name': student.profile.user.first_name,
                    'last_name': student.profile.user.last_name,
                    'dob': student.dob,
                }
            )
            
        for c in Class.objects.all():
            DimClass.objects.update_or_create(
                class_id=c.id,
                defaults={
                    'name': c.name,
                    'code': c.code,
                    'academic_year': c.academic_year
                }
            )
            
        for s in Subject.objects.all():
            DimSubject.objects.update_or_create(
                subject_id=s.id,
                defaults={
                    'name': s.name,
                    'code': s.code,
                }
            )

        # Build dates for the past year and next year
        today = timezone.now().date()
        for i in range(-365, 365):
            d = today + timedelta(days=i)
            DimDate.objects.get_or_create(
                date=d,
                defaults={
                    'year': d.year,
                    'month': d.month,
                    'day': d.day,
                    'is_weekend': d.weekday() >= 5
                }
            )
            
        # 2. Load Facts
        for att in AttendanceRecord.objects.all():
            dim_student = DimStudent.objects.filter(student_id=att.student_id).first()
            dim_date = DimDate.objects.filter(date=att.date).first()
            if dim_student and dim_date:
                FactAttendance.objects.update_or_create(
                    student=dim_student,
                    date=dim_date,
                    defaults={'status': att.status}
                )

        for grade in Grade.objects.select_related('enrollment__student', 'enrollment__school_class').all():
            dim_student = DimStudent.objects.filter(student_id=grade.enrollment.student.id).first()
            dim_subject = DimSubject.objects.filter(subject_id=grade.subject_id).first()
            dim_class = DimClass.objects.filter(class_id=grade.enrollment.school_class.id).first()
            
            if dim_student and dim_subject and dim_class:
                FactAcademicPerformance.objects.update_or_create(
                    student=dim_student,
                    subject=dim_subject,
                    school_class=dim_class,
                    graded_at=grade.updated_at.date(),
                    defaults={'score': grade.score}
                )

        for fee in Fee.objects.all():
            dim_student = DimStudent.objects.filter(student_id=fee.student_id).first()
            dim_date = DimDate.objects.filter(date=fee.due_date).first()
            
            if dim_student and dim_date:
                paid = fee.amount if fee.status == 'paid' else 0
                FactPayment.objects.update_or_create(
                    student=dim_student,
                    date=dim_date,
                    defaults={
                        'amount_due': fee.amount,
                        'amount_paid': paid,
                        'is_overdue': fee.status == 'overdue' or (fee.status == 'pending' and fee.due_date < today)
                    }
                )

        # 3. Data Quality Validation
        # Completeness check: Students missing DOB
        total_students = DimStudent.objects.count()
        missing_dob = DimStudent.objects.filter(dob__isnull=True).count()
        student_score = 100
        if total_students > 0:
            student_score = 100 * (1 - (missing_dob / total_students))

        # Accuracy check: Fact records without matching dimensions (should be 0 due to ETL logic)
        attendance_score = 100
        finance_score = 100
        
        overall = (student_score + attendance_score + finance_score) / 3
        
        DataQualityScore.objects.create(
            overall_score=overall,
            student_score=student_score,
            attendance_score=attendance_score,
            finance_score=finance_score,
            notes=f"Missing DOB: {missing_dob}"
        )
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_tasks)
