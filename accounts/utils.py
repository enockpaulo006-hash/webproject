from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string


OTP_SESSION_KEY = "seller_otp_code"
OTP_EXPIRES_KEY = "seller_otp_expires"
OTP_VERIFIED_KEY = "seller_otp_verified"
OTP_NEXT_KEY = "seller_otp_next"
OTP_ATTEMPTS_KEY = "seller_otp_attempts"
OTP_VALIDITY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
LOGIN_FAILED_ATTEMPTS_KEY = "login_failed_attempts"
LOGIN_LOCKOUT_UNTIL_KEY = "login_lockout_until"
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15

def generate_otp_code() -> str:
    return get_random_string(length=6, allowed_chars="0123456789")


def send_seller_otp_code(request, user):
    if not user.email:
        return

    otp_code = generate_otp_code()
    expires_at = timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES)
    request.session[OTP_SESSION_KEY] = otp_code
    request.session[OTP_EXPIRES_KEY] = expires_at.timestamp()
    request.session[OTP_ATTEMPTS_KEY] = 0
    request.session[OTP_VERIFIED_KEY] = False

    subject = "Seller verification code"
    message = (
        f"Your seller verification code is: {otp_code}\n\n"
        "Enter this code to continue creating or updating your listings."
    )

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def is_login_locked_out(request):
    lockout_until = request.session.get(LOGIN_LOCKOUT_UNTIL_KEY)
    if lockout_until is None:
        return False

    if timezone.now().timestamp() >= lockout_until:
        request.session.pop(LOGIN_LOCKOUT_UNTIL_KEY, None)
        request.session.pop(LOGIN_FAILED_ATTEMPTS_KEY, None)
        return False

    return True


def increment_login_failures(request):
    attempts = request.session.get(LOGIN_FAILED_ATTEMPTS_KEY, 0) + 1
    request.session[LOGIN_FAILED_ATTEMPTS_KEY] = attempts

    if attempts >= MAX_LOGIN_ATTEMPTS:
        request.session[LOGIN_LOCKOUT_UNTIL_KEY] = (
            timezone.now() + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
        ).timestamp()


def seller_otp_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get(OTP_VERIFIED_KEY):
            return view_func(request, *args, **kwargs)

        request.session[OTP_NEXT_KEY] = request.get_full_path()
        send_seller_otp_code(request, request.user)
        return redirect(reverse("accounts:verify_otp"))

    return _wrapped_view
