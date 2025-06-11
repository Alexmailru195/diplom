"""
URL configuration for shop_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from shop_project import views as main_views
from users import views as user_views
from products import views as product_views
from cart import views as cart_views

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # API маршруты (все в одном месте)
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('pos.urls')),
    path('api/', include('notifications.urls')),

    # Пользователи
    path('users/', include('users.urls')),

    # Главная страница
    path('', main_views.home, name='home'),  # ← Главная после входа

    # Альтернативные маршруты (можно удалить, если используете include)
    path('users/login/', user_views.login_view, name='login'),
    path('users/logout/', user_views.logout_view, name='logout'),
    path('users/register/', user_views.register_view, name='register'),
    path('users/profile/', user_views.profile_view, name='profile'),
    path('products/', product_views.product_list, name='products'),
    path('cart/', cart_views.cart_view, name='cart_view'),

    # Редирект с главной, если пользователь не вошёл
    path('accounts/login/', RedirectView.as_view(url='/users/login/')),
]
