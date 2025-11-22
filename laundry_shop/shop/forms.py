from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile,Service,Branch,Order

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'profile_image', 'city']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price (optional)'}),
        }

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone (optional)'}),
        }

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_name', 'delivery_address', 'delivery_phone', 'special_instructions']
        widgets = {
            'delivery_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name for delivery'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full delivery address'}),
            'delivery_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone number'}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Special instructions (optional)'}),
        }
