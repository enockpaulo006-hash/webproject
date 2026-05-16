from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ProfileUpdateForm, UserLoginForm, UserRegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            authenticated_user = authenticate(
                request,
                email=user.email,
                password=form.cleaned_data["password"],
            )
            messages.success(request, "Your account has been created successfully.")
            if authenticated_user is not None:
                login(request, authenticated_user)
            return redirect("core:home")
    else:
        form = UserRegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
            "google_auth_enabled": settings.GOOGLE_AUTH_ENABLED,
        },
    )


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["google_auth_enabled"] = settings.GOOGLE_AUTH_ENABLED
        return context

    def form_valid(self, form):
        messages.success(self.request, "You have logged in successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if user.can_access_admin_panel:
            return reverse("admin:index")
        return "/"


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect("core:home")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})
