from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm, UserSiteSettingsForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Your account has been created. You can now log in.")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        if "profile_submit" in request.POST:
            user_update_form = UserUpdateForm(request.POST, instance=request.user)
            profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            if profile_update_form.is_valid() and user_update_form.is_valid():
                user_update_form.save(), profile_update_form.save()
                messages.success(request, f"Profile updated successfully.")
                return redirect("profile")
        elif 'settings_submit' in request.POST:
            settings_update_form = UserSiteSettingsForm(request.POST, instance=request.user.setting)
            if settings_update_form.is_valid():
                settings_update_form.save()
                messages.success(request, f"Settings updated successfully.")
                return redirect("profile")
    else:
        user_update_form = UserUpdateForm(instance=request.user)
        profile_update_form = ProfileUpdateForm(instance=request.user.profile)
        settings_update_form = UserSiteSettingsForm(instance=request.user.setting)

    context = {
        "u_form": user_update_form,
        "p_form": profile_update_form,
        "s_form": settings_update_form
    }

    return render(request, "users/profile.html", context)
