"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from django.shortcuts import render, redirect
from django.http import (HttpRequest, HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import json
import io

from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
                     Lecture, QRCodeUpload, is_instructor, is_student)

#from .models import (getUploadsForCourse)

CDT = ZoneInfo("America/Chicago")

# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------


def new_user(request):
    if request.method == "GET":
        return render(request, 'app/new.html')
    else:
        return HttpResponse("Method Not Allowed", status=403)

@csrf_exempt
def createUser(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        student = request.POST.get("is_student")

        if User.objects.filter(email=email).exists():
            return HttpResponse("Email taken", status=400)

        someone = User.objects.create_user(username=user_name, email=email, password=password)

        if student == "1":
            StudentProfile.objects.create(user=someone)
        else:
            InstructorProfile.objects.create(user=someone)

        login(request, someone)

        return HttpResponse("Success", status=200)
    else:
        return HttpResponse("Method Not Allowed", status=403)



# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------
