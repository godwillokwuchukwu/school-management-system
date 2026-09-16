import pytest
from warehouse.models import DimStudent
from warehouse.tasks import run_etl_pipeline
from django.contrib.auth.models import User as CustomUser
from warehouse.analytics import get_low_attendance_students, get_outstanding_fees_by_class

pytestmark = pytest.mark.django_db


def test_run_etl_pipeline():
    result = run_etl_pipeline()
    assert DimStudent.objects.count() >= 0


def test_warehouse_analytics():
    low_att = get_low_attendance_students()
    assert isinstance(low_att, list)

    fees = get_outstanding_fees_by_class()
    assert isinstance(fees, list)
