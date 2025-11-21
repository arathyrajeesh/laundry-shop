from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProfileForm,BranchForm,ServiceForm
# NOTE: Assuming you have Profile, Order, and LaundryShop models
from .models import Profile, Order, LaundryShop ,Service,Branch
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse # Added for placeholder views
from django.db.models import Count, Q
from datetime import datetime
from django.views.decorators.http import require_POST
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
        city = request.POST.get("city")

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
        profile.city = city
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
            profile.city = request.POST.get("city")

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

    # Handle search functionality
    search_query = request.GET.get('search', '')
    services_nearby = []
    shops_nearby = []
    user_city = None

    # Check if user has city data
    try:
        user_profile = request.user.profile
        user_city = user_profile.city if user_profile.city else None
    except:
        user_city = None

    if search_query:
        # Search for services by name and get nearby branches
        services = Service.objects.filter(
            Q(name__icontains=search_query)
        ).select_related('branch__shop').filter(branch__shop__is_approved=True)

        # If user has city, prioritize services from same city
        if user_city:
            city_services = services.filter(branch__shop__city__iexact=user_city)[:10]
            if city_services:
                services_nearby = city_services
            else:
                # If no services in user's city, show all matching services
                services_nearby = services[:10]
        else:
            services_nearby = services[:10]  # Limit to 10 results
    elif user_city:
        # Show services and shops from user's city only if user has city set
        services_nearby = Service.objects.filter(
            branch__shop__is_approved=True,
            branch__shop__city__iexact=user_city
        ).select_related('branch__shop')[:10]

        # Also get shops in user's city
        shops_nearby = LaundryShop.objects.filter(
            is_approved=True,
            city__iexact=user_city
        )[:10]
    # If no search query and no city, services_nearby and shops_nearby remain empty

    return render(request, "user_dashboard.html", {
        "pending_count": pending,
        "completed_count": completed,
        "total_spent": spent,
        "shops": DUMMY_SHOPS,         # Added for the 'Current Available Laundry Shops' section
        "cloth_status": cloth_status, # Added for the 'Your Cloth Status' table
        "services_nearby": services_nearby,
        "shops_nearby": shops_nearby,
        "search_query": search_query,
        "user_city": user_city,
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
    shop = get_object_or_404(LaundryShop, id=shop_id, is_approved=True)

    # Get all branches for this shop
    branches = Branch.objects.filter(shop=shop).prefetch_related('services')

    # If shop has only one branch, redirect to branch detail
    if branches.count() == 1:
        return redirect('branch_detail', branch_id=branches.first().id)

    # Get all services across all branches
    all_services = Service.objects.filter(branch__shop=shop).select_related('branch')

    context = {
        'shop': shop,
        'branches': branches,
        'all_services': all_services,
    }

    return render(request, 'shop_detail.html', context)


@login_required
def branch_detail(request, branch_id):
    """Renders a single branch's detail page."""
    branch = get_object_or_404(Branch, id=branch_id, shop__is_approved=True)

    # Get all services for this branch
    services = Service.objects.filter(branch=branch)

    context = {
        'branch': branch,
        'shop': branch.shop,
        'services': services,
    }

    return render(request, 'branch_detail.html', context)


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
    pending_approvals = LaundryShop.objects.filter(is_approved=False).count()
    
    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user', 'shop').order_by('-created_at')[:10]
    
    # Orders by status
    orders_by_status = Order.objects.values('cloth_status').annotate(count=Count('id')).order_by('cloth_status')
    
    # Recent users (last 5)
    recent_users = User.objects.order_by('-date_joined')[:5]

    # Branches
    total_branches = Branch.objects.count()
    recent_branches = Branch.objects.select_related('shop').order_by('-created_at')[:10]

    # Shops with their branches
    shops_with_branches = LaundryShop.objects.prefetch_related('branches').all()

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
        'pending_approvals': pending_approvals,
        'total_branches': total_branches,

        # Data
        'recent_orders': recent_orders,
        'orders_by_status': orders_by_status,
        'recent_users': recent_users,
        'recent_branches': recent_branches,
        'all_shops': LaundryShop.objects.all(),
        'shops_with_branches': shops_with_branches,
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


@login_required
@user_passes_test(is_staff_user, login_url='login')
def admin_approve_shop(request, shop_id):
    """Approve a shop."""
    if request.method == 'POST':
        shop = get_object_or_404(LaundryShop, id=shop_id)
        shop.is_approved = True
        shop.save()
        return JsonResponse({'success': True, 'message': 'Shop approved successfully'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_staff_user, login_url='login')
def admin_reject_shop(request, shop_id):
    """Reject a shop."""
    if request.method == 'POST':
        shop = get_object_or_404(LaundryShop, id=shop_id)
        shop.delete()  # Or set is_approved=False and is_open=False
        return JsonResponse({'success': True, 'message': 'Shop rejected and removed'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


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
        latitude = request.POST.get("latitude", "")
        longitude = request.POST.get("longitude", "")
        city = request.POST.get("city", "")

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
            phone=phone,
            city=city,
            latitude=latitude,
            longitude=longitude,
            is_approved=False
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
                if not shop.is_approved:
                    messages.error(request, "Your shop is pending approval. Please wait for admin approval.")
                    return redirect("shop_login")
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

    # Branches
    branches = Branch.objects.filter(shop=shop).prefetch_related('services')

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
        'branches': branches,
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



# ---------- Branch Views ----------
@shop_login_required
def add_branch(request):
    shop_id = request.session.get('shop_id')
    shop = get_object_or_404(LaundryShop, id=shop_id)

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save(commit=False)
            branch.shop = shop
            branch.save()
            messages.success(request, 'Branch created successfully.')
            return redirect('shop_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BranchForm()

    return render(request, 'add_branch.html', {'form': form, 'shop': shop})


@shop_login_required
def edit_branch(request, branch_id):
    shop_id = request.session.get('shop_id')
    shop = get_object_or_404(LaundryShop, id=shop_id)
    branch = get_object_or_404(Branch, id=branch_id, shop=shop)

    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated.')
            return redirect('shop_dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = BranchForm(instance=branch)

    return render(request, 'edit_branch.html', {'form': form, 'shop': shop, 'branch': branch})


@shop_login_required
@require_POST
def delete_branch(request, branch_id):
    shop_id = request.session.get('shop_id')
    shop = get_object_or_404(LaundryShop, id=shop_id)
    branch = get_object_or_404(Branch, id=branch_id, shop=shop)
    branch.delete()
    messages.success(request, 'Branch deleted.')
    return redirect('shop_dashboard')


# ---------- Service Views ----------
@shop_login_required
def add_service(request, branch_id):
    shop_id = request.session.get('shop_id')
    shop = get_object_or_404(LaundryShop, id=shop_id)
    branch = get_object_or_404(Branch, id=branch_id, shop=shop)

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.branch = branch
            try:
                service.save()
                messages.success(request, 'Service added successfully.')
                return redirect('shop_dashboard')
            except IntegrityError:
                messages.error(request, 'This service already exists for this branch.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceForm()

    return render(request, 'add_service.html', {'form': form, 'shop': shop, 'branch': branch})


@shop_login_required
@require_POST
def delete_service(request, service_id):
    shop_id = request.session.get('shop_id')
    shop = get_object_or_404(LaundryShop, id=shop_id)
    service = get_object_or_404(Service, id=service_id, branch__shop=shop)
    service.delete()
    messages.success(request, 'Service deleted.')
    return redirect('shop_dashboard')