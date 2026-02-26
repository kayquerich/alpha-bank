from django.db import models
from clientbank.models.Client import Client

class Order(models.Model):
    
    STATUS_CHOICES = [
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Gera número do pedido (formato: ORD-YYYYMMDD-XXXXX)
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(order_number__startswith=f'ORD-{date_str}').order_by('-order_number').first()
            
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.order_number = f'ORD-{date_str}-{new_number:05d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pedido {self.order_number} - {self.client.user.first_name}"
    
    def get_items_count(self):
        return self.items.count()
    
    def get_status_display_color(self):
        colors = {
            'processing': '#3b82f6',
            'completed': '#10b981',
            'cancelled': '#ef4444',
        }
        return colors.get(self.status, '#6b7280')
