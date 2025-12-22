from django.db import models

class Product(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
    