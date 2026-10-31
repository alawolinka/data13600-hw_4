from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo
from django.shortcuts import render

from django.http import HttpRequest, HttpResponse

CDT = ZoneInfo("America/Chicago")


def time_view(request: HttpRequest) -> HttpResponse:
    """Return current Chicago time as HH:MM (24-hour), plain text."""
    now = datetime.now(tz=CDT)
    return HttpResponse(now.strftime("%H:%M"), content_type="text/plain")


def _decimal_to_str(x: Decimal) -> str:
    """Format Decimal without scientific notation and without trailing zeros."""
    s = format(x, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def sum_view(request: HttpRequest) -> HttpResponse:
    """Return n1 + n2 from query params as plain text."""
    n1_str = request.GET.get("n1", "0")
    n2_str = request.GET.get("n2", "0")

    try:
        val = Decimal(n1_str) + Decimal(n2_str)
    except (InvalidOperation, ValueError):
        return HttpResponse("Bad Request: n1 and n2 must be numbers", status=400, content_type="text/plain")

    return HttpResponse(_decimal_to_str(val), content_type="text/plain")

def index(request):
    """Render the home page (index.html)."""
    now = datetime.now(tz=CDT).strftime("%H:%M")
    context = {"current_time": now}
    return render(request, 'app/index.html', context)