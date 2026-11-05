"""Public pages of the core application (privacy notice)."""
from django.shortcuts import render

PRIVACY_NOTICE_VERSION = "1.1"
PRIVACY_NOTICE_DATE = "November 2026"


def privacy_notice(request):
    """The privacy notice every visitor can read before creating an account."""
    return render(
        request,
        "privacy/notice.html",
        {
            "notice_version": PRIVACY_NOTICE_VERSION,
            "notice_date": PRIVACY_NOTICE_DATE,
        },
    )
