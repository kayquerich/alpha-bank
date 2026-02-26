from django.db import models
from ecommerce.models.Product import Product
from ecommerce.models.Order import Order

class OrderItem(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)  # Salva o nome do produto no momento da compra
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Salva o preço no momento da compra
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
    
    def get_subtotal(self):
        return self.product_price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} - Pedido {self.order.order_number}"
