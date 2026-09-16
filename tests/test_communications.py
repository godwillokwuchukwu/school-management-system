import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from communications.models import (
    Announcement,
    Conversation,
    ConversationParticipant,
    Message,
)

User = get_user_model()


@pytest.fixture
def teacher_client():
    client = APIClient()
    teacher = User.objects.create_user(
        "teacher_comm@example.com", "teacher_comm@example.com", "Pass12345!"
    )
    teacher.profile.role = "teacher"
    teacher.profile.save()
    client.force_authenticate(user=teacher)
    return client, teacher


@pytest.fixture
def student_client():
    client = APIClient()
    student = User.objects.create_user(
        "student_comm@example.com", "student_comm@example.com", "Pass12345!"
    )
    student.profile.role = "student"
    student.profile.save()
    client.force_authenticate(user=student)
    return client, student


@pytest.mark.django_db
def test_announcements_and_conversations(teacher_client, student_client):
    t_client, teacher = teacher_client
    s_client, student = student_client

    # Teacher creates announcement for all
    ann_resp = t_client.post(
        "/api/communications/announcements/",
        {
            "title": "Welcome Back Assembly",
            "content": "All students report to the auditorium.",
            "category": "school-wide",
            "target_all": True,
            "created_by": teacher.id,
        },
        format="json",
    )
    assert ann_resp.status_code == 201

    # Student reads announcement
    s_ann_resp = s_client.get("/api/communications/announcements/")
    assert s_ann_resp.status_code == 200
    assert len(s_ann_resp.data["results"]) >= 1

    # Conversation setup
    conv = Conversation.objects.create(subject="Homework Question")
    ConversationParticipant.objects.create(conversation=conv, user=teacher)
    ConversationParticipant.objects.create(conversation=conv, user=student)

    # Student replies to conversation
    reply_resp = s_client.post(
        f"/api/communications/conversations/{conv.id}/reply/",
        {"body": "Hello, I have a question about exercise 3."},
        format="json",
    )
    assert reply_resp.status_code in (200, 201)
    assert Message.objects.filter(conversation=conv).count() == 1


@pytest.mark.django_db
def test_send_email_notification_task():
    from communications.tasks import send_email_notification

    res = send_email_notification("Test Subject", "Test Body", ["test@example.com"])
    assert res is True
