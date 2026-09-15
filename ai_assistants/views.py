import json
import os
import sys
import urllib.error
import urllib.request

from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAdminOrTeacher
from .models import AIAuditLog

TESTING = "pytest" in sys.modules


# Real Gemini API call with multi-model fallback cascade
CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
]


def call_gemini_api(prompt, context=""):
    if TESTING:
        return f"[TEST] Response to: {prompt[:30]}"

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return (
            "[MOCK] Gemini API Key not set. Simulated response based on context: "
            + context[:50]
            + "..."
        )

    full_prompt = (
        f"Context:\n{context}\n\nUser Question:\n{prompt}" if context else prompt
    )
    payload = json.dumps(
        {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800},
        }
    ).encode("utf-8")

    last_error = None
    for model_name in CANDIDATE_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception as exc:
            last_error = exc
            continue

    return f"AI Assistant temporarily unavailable ({last_error}). Please try again shortly."


class ChatbotView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response(
                {"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Mock RAG retrieval
        context = "School Policy: Attendance is mandatory. Fees are due on the 1st."

        # Guardrail: Prevent requesting another student's data
        if "other student" in prompt.lower() or "grade of" in prompt.lower():
            context = "I can only provide information about your own account and general school policies."

        response_text = call_gemini_api(prompt, context)

        AIAuditLog.objects.create(
            user=request.user,
            assistant_type="chatbot",
            prompt=prompt,
            response=response_text,
            context_used=context,
        )

        return Response({"response": response_text})


class TeacherAssistantView(views.APIView):
    permission_classes = [IsAdminOrTeacher]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response(
                {"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST
            )

        context = "Teacher Guidelines: Draft lesson plans and rubrics."
        response_text = call_gemini_api(prompt, context)

        AIAuditLog.objects.create(
            user=request.user,
            assistant_type="teacher",
            prompt=prompt,
            response=response_text,
            context_used=context,
        )

        return Response(
            {
                "response": response_text,
                "notice": "Draft generated. Human review is mandatory before publishing.",
            }
        )


class AdminAssistantView(views.APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response(
                {"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST
            )

        context = "Admin Guidelines: Controlled queries against approved datasets."
        response_text = call_gemini_api(prompt, context)

        AIAuditLog.objects.create(
            user=request.user,
            assistant_type="admin",
            prompt=prompt,
            response=response_text,
            context_used=context,
        )

        return Response({"response": response_text})


class ExplainerAssistantView(views.APIView):
    permission_classes = [IsAdminOrTeacher]

    def post(self, request):
        prompt = request.data.get("prompt")  # e.g. Student ID
        if not prompt:
            return Response(
                {"error": "Prompt required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # In reality this fetches the SHAP output from Stage 8
        context = (
            "SHAP Output: Low attendance (30% impact), Declining grades (20% impact)."
        )

        system_instruction = (
            "Summarize the factors. Do not diagnose or make disciplinary decisions."
        )
        response_text = call_gemini_api(system_instruction + " " + prompt, context)

        AIAuditLog.objects.create(
            user=request.user,
            assistant_type="explainer",
            prompt=prompt,
            response=response_text,
            context_used=context,
        )

        return Response(
            {
                "response": response_text,
                "disclaimer": "This is an AI summary of predictive factors. It is not a settled fact.",
            }
        )
