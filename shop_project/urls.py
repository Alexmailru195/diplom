# shop_project/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views

from shop_project.views import home_view

urlpatterns = [
    # === Админка ===
    path('admin/', admin.site.urls),

    # === Основные маршруты ===
    path('', home_view, name='home'),
    path('', include('products.urls')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('users/', include('users.urls')),
    path('logout/', views.logout_view, name='logout'),
    path('notifications/', include('notifications.urls')),
    path('pos/', include('pos.urls')),
    path('inventory/', include('inventory.urls')),
]

# === Обслуживание медиафайлов (только для разработки) ===
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)