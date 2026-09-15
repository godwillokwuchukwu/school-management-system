from django.urls import path
from .views import (
    ChatbotView,
    TeacherAssistantView,
    AdminAssistantView,
    ExplainerAssistantView,
)

urlpatterns = [
    path("chatbot/", ChatbotView.as_view(), name="ai-chatbot"),
    path("teacher/", TeacherAssistantView.as_view(), name="ai-teacher"),
    path("admin/", AdminAssistantView.as_view(), name="ai-admin"),
    path("explainer/", ExplainerAssistantView.as_view(), name="ai-explainer"),
]
