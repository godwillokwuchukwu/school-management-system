import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\ai_assistants\views.py"

new_views = """
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AIAuditLog
from accounts.permissions import IsAdmin, IsAdminOrTeacher
import os

# Stub for the Gemini API call
def call_gemini_api(prompt, context):
    # In a real implementation this would use google-genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "[MOCK] Gemini API Key not set. Simulated response based on context: " + context[:50] + "..."
    return f"[MOCK] Simulated response to: {prompt[:30]}..."

class ChatbotView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST)

        # Mock RAG retrieval
        context = "School Policy: Attendance is mandatory. Fees are due on the 1st."
        
        # Guardrail: Prevent requesting another student's data
        if "other student" in prompt.lower() or "grade of" in prompt.lower():
            context = "I can only provide information about your own account and general school policies."
            
        response_text = call_gemini_api(prompt, context)
        
        AIAuditLog.objects.create(
            user=request.user,
            assistant_type='chatbot',
            prompt=prompt,
            response=response_text,
            context_used=context
        )
        
        return Response({"response": response_text})

class TeacherAssistantView(views.APIView):
    permission_classes = [IsAdminOrTeacher]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST)

        context = "Teacher Guidelines: Draft lesson plans and rubrics."
        response_text = call_gemini_api(prompt, context)
        
        AIAuditLog.objects.create(
            user=request.user,
            assistant_type='teacher',
            prompt=prompt,
            response=response_text,
            context_used=context
        )
        
        return Response({
            "response": response_text,
            "notice": "Draft generated. Human review is mandatory before publishing."
        })

class AdminAssistantView(views.APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST)

        context = "Admin Guidelines: Controlled queries against approved datasets."
        response_text = call_gemini_api(prompt, context)
        
        AIAuditLog.objects.create(
            user=request.user,
            assistant_type='admin',
            prompt=prompt,
            response=response_text,
            context_used=context
        )
        
        return Response({"response": response_text})

class ExplainerAssistantView(views.APIView):
    permission_classes = [IsAdminOrTeacher]

    def post(self, request):
        prompt = request.data.get("prompt") # e.g. Student ID
        if not prompt:
            return Response({"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST)

        # In reality this fetches the SHAP output from Stage 8
        context = "SHAP Output: Low attendance (30% impact), Declining grades (20% impact)."
        
        system_instruction = "Summarize the factors. Do not diagnose or make disciplinary decisions."
        response_text = call_gemini_api(system_instruction + " " + prompt, context)
        
        AIAuditLog.objects.create(
            user=request.user,
            assistant_type='explainer',
            prompt=prompt,
            response=response_text,
            context_used=context
        )
        
        return Response({
            "response": response_text,
            "disclaimer": "This is an AI summary of predictive factors. It is not a settled fact."
        })
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_views)
