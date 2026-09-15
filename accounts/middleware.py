class AuditLogMiddleware:
    """
    No request/response mutation — this exists purely so `accounts.audit`
    and any view can rely on `request.META` having a consistently resolved
    client IP (respecting X-Forwarded-For behind a proxy/load balancer)
    without every call site re-deriving it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        request.client_ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else request.META.get("REMOTE_ADDR")
        )
        return self.get_response(request)
