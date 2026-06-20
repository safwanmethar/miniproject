from django.contrib import admin
from .models import Customer, Category, Brand, Product, Cart

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Cart)