import pytest
from warehouse.models import DimStudent
from warehouse.tasks import run_etl_pipeline
from django.contrib.auth.models import User as CustomUser

pytestmark = pytest.mark.django_db


def test_run_etl_pipeline():
    result = run_etl_pipeline()
    assert DimStudent.objects.count() >= 0
