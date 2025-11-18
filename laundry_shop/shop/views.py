from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings


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
            return redirect("home")
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
        user.save()

        # Save profile info
        profile = Profile.objects.get(user=user)
        profile.latitude = latitude
        profile.longitude = longitude
        profile.save()

        # ---------------------------------
        # ✅ Send Welcome Email
        # ---------------------------------
        welcome_message = f"""
Hi {username},

Welcome to our Bright & Shine! 🎉

Your account has been created successfully.

We are excited to have you with us. You can now log in and start using all features of our platform.

If you ever need help, feel free to contact us anytime.

Have a great day! 😊
"""

        send_mail(
            subject="🎉 Welcome to Bright & Shine",
            message=welcome_message,
            from_email=settings.EMAIL_HOST_USER,   # use your Gmail
            recipient_list=[email],
            fail_silently=False,
        )
        # ---------------------------------

        messages.success(request, "Account created successfully! Check your email.")
        return redirect("login")

    return render(request, "signup.html")
