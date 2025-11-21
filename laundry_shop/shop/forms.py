from django import forms
from .models import Profile,Service,Branch

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'profile_image']


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
