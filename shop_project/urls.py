# shop_project/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from products.views import product_list_view
from . import views

from shop_project.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главная страница
    path('', home_view, name='home'),  # ← только один раз пустой маршрут

    # Приложения
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('users/', include('users.urls')),
    path('logout/', views.logout_view, name='logout'),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    path('pos/', include(('pos.urls', 'pos'), namespace='pos')),
    path('inventory/', include(('inventory.urls', 'inventory'), namespace='inventory')),
]

# === Обслуживание медиафайлов (только для разработки) ===
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)