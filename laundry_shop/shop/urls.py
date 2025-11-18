from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication & Home ---
    path('', views.hero, name='home'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    
    # --- Dashboard & Profile ---
    path("dashboard/", views.user_dashboard, name="dashboard"),
    
    # This URL is for the 'View Profile' link in the dropdown and for direct access
    path('profile/', views.profile_detail, name='profile_detail'), 
    
    # NOTE: Renamed to avoid clash, as 'profile' was used for profile_page originally
    path("profile/edit/", views.edit_profile, name="edit_profile"), 
    
    
    # --- NEW DROPDOWN LINKS ---
    path('settings/', views.settings_view, name='settings'),
    path('help/', views.help_view, name='help'),
    path('language/', views.language_settings, name='language_settings'),
    path('orders/', views.my_orders, name='orders'),
    path('billing/', views.billing_payments, name='billing'),
    
    # --- Shop Detail (Link from Dashboard) ---
    path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
]