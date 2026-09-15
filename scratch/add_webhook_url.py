import re

file_path = r"c:\Users\Godwill\Downloads\school-management-system-stage2-riverside\school-management-system\fees\urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from .views import FeeViewSet", "from .views import FeeViewSet, PaymentWebhookView"
)

if "PaymentWebhookView.as_view()" not in content:
    content = content.replace(
        'urlpatterns = [path("", include(router.urls))]',
        'urlpatterns = [\n    path("webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),\n    path("", include(router.urls)),\n]',
    )

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
