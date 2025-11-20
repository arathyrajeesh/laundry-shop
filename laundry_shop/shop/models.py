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

    def __str__(self):
        return self.user.username



class LaundryShop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    address = models.TextField()
    is_open = models.BooleanField(default=True)
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
    cloth_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
