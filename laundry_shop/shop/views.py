from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProfileForm
# NOTE: Assuming you have Profile, Order, and LaundryShop models
from .models import Profile, Order, LaundryShop 
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum      
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse # Added for placeholder views
from django.db.models import Count, Q
from datetime import datetime, timedelta

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
        return [{'cloth_name': f"Order #{order.id}", 'status': order.cloth_status, 'delivery_date': order.created_at} for order in orders]
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
            # Redirect to 'next' parameter if present, otherwise check user type
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            # Redirect staff/superusers to admin dashboard, regular users to user dashboard
            elif user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            # Preserve the 'next' parameter in the redirect
            next_param = request.GET.get('next', '')
            if next_param:
                return redirect(f"{reverse('login')}?next={next_param}")
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
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
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


# --- ADMIN DASHBOARD VIEWS ---

def is_staff_user(user):
    """Check if user is staff or superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_staff_user, login_url='login')
def admin_dashboard(request):
    """Admin dashboard with statistics and management tools."""
    
    # Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(cloth_status="Pending").count()
    completed_orders = Order.objects.filter(cloth_status="Completed").count()
    washing_orders = Order.objects.filter(cloth_status="Washing").count()
    ready_orders = Order.objects.filter(cloth_status="Ready").count()
    
    # Revenue
    total_revenue = Order.objects.aggregate(total=Sum('amount'))['total'] or 0
    today_revenue = Order.objects.filter(
        created_at__date=datetime.now().date()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Users
    total_users = User.objects.count()
    new_users_today = User.objects.filter(
        date_joined__date=datetime.now().date()
    ).count()
    
    # Shops
    total_shops = LaundryShop.objects.count()
    open_shops = LaundryShop.objects.filter(is_open=True).count()
    
    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user', 'shop').order_by('-created_at')[:10]
    
    # Orders by status
    orders_by_status = Order.objects.values('cloth_status').annotate(count=Count('id')).order_by('cloth_status')
    
    # Recent users (last 5)
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        # Statistics
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'washing_orders': washing_orders,
        'ready_orders': ready_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'total_shops': total_shops,
        'open_shops': open_shops,
        
        # Data
        'recent_orders': recent_orders,
        'orders_by_status': orders_by_status,
        'recent_users': recent_users,
        'all_shops': LaundryShop.objects.all(),
    }
    
    return render(request, 'admin_dashboard.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='login')
def admin_update_order_status(request, order_id):
    """Update order status (AJAX endpoint)."""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.cloth_status = new_status
            order.save()
            return JsonResponse({'success': True, 'message': 'Order status updated successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_staff_user, login_url='login')
def admin_orders(request):
    """View all orders with filtering."""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    orders = Order.objects.select_related('user', 'shop').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(cloth_status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_orders.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='login')
def admin_users(request):
    """View all users."""
    search_query = request.GET.get('search', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    
    return render(request, 'admin_users.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='login')
def admin_shops(request):
    """View and manage shops."""
    shops = LaundryShop.objects.all().order_by('name')
    
    context = {
        'shops': shops,
    }
    
    return render(request, 'admin_shops.html', context)


# --- SHOP AUTHENTICATION VIEWS ---

def shop_register(request):
    """Shop registration page."""
    if request.method == "POST":
        shop_name = request.POST.get("shop_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        address = request.POST.get("address", "")
        phone = request.POST.get("phone", "")

        # Validation
        if not shop_name or not email or not password1 or not password2:
            messages.error(request, "All fields are required")
            return redirect("shop_register")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("shop_register")

        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters long")
            return redirect("shop_register")

        if LaundryShop.objects.filter(name=shop_name).exists():
            messages.error(request, "Shop name already taken")
            return redirect("shop_register")

        if LaundryShop.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("shop_register")

        # Create shop
        shop = LaundryShop(
            name=shop_name,
            email=email,
            address=address,
            phone=phone
        )
        shop.set_password(password1)
        shop.save()

        messages.success(request, "Shop registered successfully! Please login.")
        return redirect("shop_login")

    return render(request, "shop_register.html")


def shop_login(request):
    """Shop login page."""
    if request.method == "POST":
        shop_name = request.POST.get("shop_name")
        password = request.POST.get("password")

        if not shop_name or not password:
            messages.error(request, "Please enter both shop name and password")
            return redirect("shop_login")

        try:
            shop = LaundryShop.objects.get(name=shop_name)
            if shop.check_password(password):
                # Store shop ID in session
                request.session['shop_id'] = shop.id
                request.session['shop_name'] = shop.name
                messages.success(request, f"Welcome back, {shop.name}!")
                return redirect("shop_dashboard")
            else:
                messages.error(request, "Invalid shop name or password")
        except LaundryShop.DoesNotExist:
            messages.error(request, "Invalid shop name or password")

        return redirect("shop_login")

    return render(request, "shop_login.html")


def shop_logout(request):
    """Shop logout."""
    if 'shop_id' in request.session:
        shop_name = request.session.get('shop_name', 'Shop')
        del request.session['shop_id']
        del request.session['shop_name']
        messages.success(request, f"Logged out successfully from {shop_name}")
    return redirect("shop_login")


def is_shop_logged_in(request):
    """Check if shop is logged in."""
    return 'shop_id' in request.session


def shop_login_required(view_func):
    """Decorator to require shop login."""
    from functools import wraps
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_shop_logged_in(request):
            messages.error(request, "Please login to access this page")
            return redirect("shop_login")
        return view_func(request, *args, **kwargs)
    return wrapper


@shop_login_required
def shop_dashboard(request):
    """Shop dashboard."""
    shop_id = request.session.get('shop_id')
    shop = get_object_or_404(LaundryShop, id=shop_id)
    
    # Get shop's orders
    shop_orders = Order.objects.filter(shop=shop).order_by('-created_at')
    
    # Statistics
    total_orders = shop_orders.count()
    pending_orders = shop_orders.filter(cloth_status="Pending").count()
    washing_orders = shop_orders.filter(cloth_status="Washing").count()
    drying_orders = shop_orders.filter(cloth_status="Drying").count()
    ironing_orders = shop_orders.filter(cloth_status="Ironing").count()
    ready_orders = shop_orders.filter(cloth_status="Ready").count()
    completed_orders = shop_orders.filter(cloth_status="Completed").count()
    total_revenue = shop_orders.aggregate(total=Sum('amount'))['total'] or 0
    
    # Today's revenue
    today_revenue = shop_orders.filter(
        created_at__date=datetime.now().date()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent orders
    recent_orders = shop_orders.select_related('user')[:10]
    
    context = {
        'shop': shop,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'washing_orders': washing_orders,
        'drying_orders': drying_orders,
        'ironing_orders': ironing_orders,
        'ready_orders': ready_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'shop_dashboard.html', context)


@shop_login_required
def shop_update_order_status(request, order_id):
    """Update order status for shop (AJAX endpoint)."""
    if request.method == 'POST':
        shop_id = request.session.get('shop_id')
        shop = get_object_or_404(LaundryShop, id=shop_id)
        order = get_object_or_404(Order, id=order_id)
        
        # Verify that the order belongs to this shop
        if order.shop != shop:
            return JsonResponse({'success': False, 'message': 'You do not have permission to update this order'}, status=403)
        
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.cloth_status = new_status
            order.save()
            return JsonResponse({'success': True, 'message': 'Order status updated successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)