import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\warehouse\analytics.py"

new_analytics = """
from django.db import connection

def get_low_attendance_students():
    query = '''
        SELECT s.first_name, s.last_name, 
               COUNT(f.id) as total_days,
               SUM(CASE WHEN f.status = 'present' THEN 1 ELSE 0 END) as present_days,
               CAST(SUM(CASE WHEN f.status = 'present' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(f.id) * 100 as attendance_pct
        FROM warehouse_factattendance f
        JOIN warehouse_dimstudent s ON f.student_id = s.id
        GROUP BY s.id, s.first_name, s.last_name
        HAVING attendance_pct < 80.0
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_outstanding_fees_by_class():
    query = '''
        SELECT c.name as class_name,
               SUM(f.amount_due - f.amount_paid) as total_outstanding
        FROM warehouse_factpayment f
        JOIN warehouse_dimstudent s ON f.student_id = s.id
        -- We need to join enrollment via operational tables or add class to DimStudent/FactPayment
        -- For now, aggregate by student
        GROUP BY c.name
    '''
    # We would build this out completely depending on exact schema connections
    pass
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_analytics)
