from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProfileForm
# NOTE: Assuming you have Profile, Order, and LaundryShop models
from .models import Profile, Order, LaundryShop 
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum      
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse # Added for placeholder views

# --- DUMMY DATA (FOR VIEWS) ---
DUMMY_SHOPS = [
    {'id': 1, 'name': 'QuickClean Laundry', 'address': '123 Main St, Kannur'},
    {'id': 2, 'name': 'SparkleWash Express', 'address': '456 Commercial Rd, Kannur'},
]

# NOTE: The dashboard template expects a 'cloth_status' list. 
# We'll use the user's last 5 orders as a stand-in.
def get_cloth_status(user):
    # Fetch actual orders and format them
    # For now, return a placeholder list if no orders exist, 
    # or fetch the last few orders
    orders = Order.objects.filter(user=user).order_by('-id')[:5]
    if orders:
        return [{'cloth_name': f"Order #{order.id}", 'status': order.cloth_status, 'delivery_date': order.expected_delivery_date} for order in orders]
    return [
        {'cloth_name': 'No recent orders', 'status': 'N/A', 'delivery_date': 'N/A'}
    ]

# --- Existing Views ---

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

        # Create Profile on Signup (NOTE: Profile should be created automatically via a signal if not here)
        # Using get_or_create defensively
        profile, created = Profile.objects.get_or_create(user=user)
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


@login_required
def user_dashboard(request):
    # Statistics from your original code
    pending = Order.objects.filter(user=request.user, cloth_status="Pending").count()
    completed = Order.objects.filter(user=request.user, cloth_status="Completed").count()

    spent = Order.objects.filter(user=request.user).aggregate(
        total=Sum('amount')
    )["total"] or 0

    # Data needed for the new dashboard template (shops and cloth status table)
    cloth_status = get_cloth_status(request.user)

    return render(request, "user_dashboard.html", {
        "pending_count": pending,
        "completed_count": completed,
        "total_spent": spent,
        "shops": DUMMY_SHOPS,         # Added for the 'Current Available Laundry Shops' section
        "cloth_status": cloth_status, # Added for the 'Your Cloth Status' table
    })

# --- NEW DROPDOWN VIEWS ---

@login_required
def profile_detail(request):
    """Renders the detailed profile page (used by 'View Profile' button in dropdown)."""
    return render(request, 'profile.html') # Reusing the existing 'profile.html' template

@login_required
def settings_view(request):
    """Renders the Settings page."""
    return render(request, 'setting.html')

@login_required
def help_view(request):
    """Renders the Help page."""
    return render(request, 'help.html')

@login_required
def language_settings(request):
    """Renders the Language Settings page."""
    return render(request, 'language_settings.html')

@login_required
def my_orders(request):
    """Renders the My Orders page."""
    # Pass user orders data here
    user_orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders.html', {'orders': user_orders})

@login_required
def billing_payments(request):
    """Renders the Billing & Payments page."""
    # Pass billing/payment data here
    return render(request, 'billing.html')

@login_required
def shop_detail(request, shop_id):
    """Renders a single laundry shop's detail page."""
    shop = get_object_or_404(LaundryShop, id=shop_id)
    return render(request, 'shop_detail.html', {'shop': shop})