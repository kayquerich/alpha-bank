from django.db import models
from clientbank.models.Client import Client

class Invoice(models.Model):

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    expiration_date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    pay = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice: {self.value} - {self.client.user.email}"