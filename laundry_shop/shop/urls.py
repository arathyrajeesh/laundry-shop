from django.urls import path
from . import views

urlpatterns = [
    path("", views.hero, name="home"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_user, name="logout"),

    # PROFILE
    path("profile/", views.profile_page, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # DASHBOARD
    path("dashboard/", views.user_dashboard, name="dashboard"),

    # SHOPS
    path("shop/<int:shop_id>/", views.shop_detail, name="shop_detail"),

    # DROPDOWN PAGES
    path("settings/", views.settings_view, name="settings"),
    path("help/", views.help_view, name="help"),
    path("language/", views.language_settings, name="language"),
    path("orders/", views.my_orders, name="orders"),
    path("billing/", views.billing_payments, name="billing"),
]
