from django.contrib import admin
from django.urls import path
from miniapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path('login/',views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/',views.register, name='register'),
    path('userhome/', views.userhome, name='userhome'),
    path('adminhome/', views.adminhome, name='adminhome'),
    path('products/',views.products, name='products'),
    path('product/<int:id>/',views.product_details, name='product_details'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('admin-home/', views.adminhome, name='adminhome'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('update-order/<int:id>/', views.update_order, name='update_order'),
    path('admin-products/', views.admin_products, name='admin_products'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),
    # Categories
    path('admin-categories/', views.admin_categories),
    path('add-category/', views.add_category),
    path('edit-category/<int:id>/', views.edit_category),
    path('delete-category/<int:id>/', views.delete_category),
    # Brands
    path('admin-brands/', views.admin_brands),
    path('add-brand/', views.add_brand),
    path('edit-brand/<int:id>/', views.edit_brand),
    path('delete-brand/<int:id>/', views.delete_brand),
    path('admin-customers/', views.admin_customers,name='admin_customers'),
    path('profile/', views.profile,name='profile'),
    path('reports/', views.reports,name='reports'),
    path('settings/', views.settings, name='settings'),
    path('admin-reviews/', views.admin_reviews, name='admin_reviews'),
    path('payment/',views.payment,name='payment'),
    path('payment/<int:order_id>/', views.payment,name='payment'),
    path('payment-success/<int:order_id>/',views.payment_success,name='payment_success'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )