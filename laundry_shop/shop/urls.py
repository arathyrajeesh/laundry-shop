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

    # ADMIN DASHBOARD
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/orders/", views.admin_orders, name="admin_orders"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/shops/", views.admin_shops, name="admin_shops"),
    path("admin/order/<int:order_id>/update-status/", views.admin_update_order_status, name="admin_update_order_status"),

    # SHOP AUTHENTICATION
    path("shop/register/", views.shop_register, name="shop_register"),
    path("shop/login/", views.shop_login, name="shop_login"),
    path("shop/logout/", views.shop_logout, name="shop_logout"),
    path("shop/dashboard/", views.shop_dashboard, name="shop_dashboard"),
    path("shop/order/<int:order_id>/update-status/", views.shop_update_order_status, name="shop_update_order_status"),
]
