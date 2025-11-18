from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProfileForm
from .models import Profile, Order     # ✅ Order added
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum       # ✅ Needed for total spent
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required


def hero(request):
    return render(request, 'home.html')


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


def signup(request):
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Password check
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("signup")

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)

        # Create Profile on Signup
        profile = Profile.objects.get(user=user)
        profile.latitude = latitude
        profile.longitude = longitude
        profile.save()

        # Send Welcome Email
        welcome_message = f"""
Hi {username},

Welcome to Bright & Shine! 🎉

Your account has been created successfully.

Enjoy our laundry services anytime — fast & clean! 🧺✨
"""

        send_mail(
            subject="🎉 Welcome to Bright & Shine",
            message=welcome_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Account created successfully! Check your email.")
        return redirect("login")

    return render(request, "signup.html")


@login_required
def profile_page(request):
    return render(request, "profile.html")


def logout_user(request):
    logout(request)
    return redirect("login")


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)

            profile.latitude = request.POST.get("latitude")
            profile.longitude = request.POST.get("longitude")

            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Invalid data submitted!")

    else:
        form = ProfileForm(instance=profile)

    return render(request, "edit_profile.html", {"form": form, "profile": profile})


# -------------------------------
# ✅ USER DASHBOARD
# -------------------------------
@login_required
def user_dashboard(request):
    pending = Order.objects.filter(user=request.user, status="Pending").count()
    completed = Order.objects.filter(user=request.user, status="Completed").count()
    spent = Order.objects.filter(user=request.user).aggregate(total=Sum('amount'))["total"] or 0

    return render(request, "user_dashboard.html", {
        "pending_count": pending,
        "completed_count": completed,
        "total_spent": spent,
    })
