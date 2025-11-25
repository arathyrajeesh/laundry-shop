from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255, default="User")
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)

    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    # Notification settings
    notifications_enabled = models.BooleanField(default=True, help_text="Enable notification badges and alerts")

    def __str__(self):
        return self.user.username



class LaundryShop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    is_open = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    phone = models.CharField(max_length=15)
    image = models.ImageField(upload_to="shops/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check if the provided password is correct."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Washing", "Washing"),
        ("Drying", "Drying"),
        ("Ironing", "Ironing"),
        ("Ready", "Ready for Pickup"),
        ("Completed", "Completed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(LaundryShop, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True)
    cloth_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Delivery details
    delivery_name = models.CharField(max_length=255, blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    delivery_phone = models.CharField(max_length=20, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)

    # Pickup and delivery dates
    pickup_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)

class Service(models.Model):
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # optional
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('branch', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


class Branch(models.Model):
    shop = models.ForeignKey(LaundryShop, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=150)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.shop.name}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order_placed', 'Order Placed'),
        ('status_update', 'Status Update'),
        ('ready_pickup', 'Ready for Pickup'),
        ('completed', 'Order Completed'),
        ('welcome', 'Welcome'),
        ('profile_reminder', 'Profile Reminder'),
        ('explore_services', 'Explore Services'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    icon = models.CharField(max_length=50, default='fas fa-bell')
    color = models.CharField(max_length=20, default='#3498db')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"