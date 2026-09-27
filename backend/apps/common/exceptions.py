from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Wrap DRF's default handler so every error body has a stable shape.

    Frontend code can rely on `{"detail": str, "code": str, "errors": dict|None}`
    instead of DRF's inconsistent per-exception-type payloads.
    """
    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(data, dict) and "detail" in data and len(data) == 1:
        payload = {"detail": str(data["detail"]), "code": getattr(exc, "default_code", "error"), "errors": None}
    else:
        payload = {"detail": "Validation failed.", "code": "validation_error", "errors": data}

    response.data = payload
    return response
