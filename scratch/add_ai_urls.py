import re

file_path_urls = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\ai_assistants\urls.py"
new_urls = """
from django.urls import path
from .views import ChatbotView, TeacherAssistantView, AdminAssistantView, ExplainerAssistantView

urlpatterns = [
    path('chatbot/', ChatbotView.as_view(), name='ai-chatbot'),
    path('teacher/', TeacherAssistantView.as_view(), name='ai-teacher'),
    path('admin/', AdminAssistantView.as_view(), name='ai-admin'),
    path('explainer/', ExplainerAssistantView.as_view(), name='ai-explainer'),
]
"""
with open(file_path_urls, "w", encoding="utf-8") as f:
    f.write(new_urls)

file_path_config = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\config\urls.py"
with open(file_path_config, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'path("api/core/", include("core.urls")),',
    'path("api/ai/", include("ai_assistants.urls")),\n    path("api/core/", include("core.urls")),',
)

with open(file_path_config, "w", encoding="utf-8") as f:
    f.write(content)
