from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    full_name = models.CharField(max_length=255, default="User")
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)

    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Completed", "Completed")])
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class LaundryShop(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    is_open = models.BooleanField(default=True)
    phone = models.CharField(max_length=15)
    image = models.ImageField(upload_to="shops/", blank=True, null=True)

    def __str__(self):
        return self.name
