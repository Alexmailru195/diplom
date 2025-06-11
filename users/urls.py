# users/urls.py

from django.urls import path
from .views import (
    register_view,
    login_view,
    profile_view,
    logout_view,
    change_password_view
)

app_name = 'users'

urlpatterns = [
    # === Django Template Views ===
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
]