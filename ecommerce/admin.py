from django.contrib import admin
from ecommerce.models.Product import Product
from ecommerce.models.Cart import Cart
from ecommerce.models.CartItem import CartItem

# Register your models here.

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)