from django.db import models
from clientbank.models.Client import Client
from ecommerce.models.Product import Product

class Cart(models.Model):

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem', blank=True, related_name='carts')

    def __str__(self):
        return f"Cart of {self.client.user.first_name} {self.client.user.last_name}"
