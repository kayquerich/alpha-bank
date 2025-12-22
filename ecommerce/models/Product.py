from django.db import models

class Product(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_discount(self):
        if self.old_price and self.old_price > self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            self.discount_percentage = round(discount, 2)
        else:
            self.discount_percentage = 0.0

    def save(self, *args, **kwargs):
        self.calculate_discount()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    