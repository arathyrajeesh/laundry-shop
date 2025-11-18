from django.urls import path
from . import views

urlpatterns = [
    path('', views.hero, name='home'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile_page, name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

]
