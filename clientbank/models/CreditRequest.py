from django.db import models
from clientbank.models.Client import Client
from management.models.Manager import Manager

class CreditRequest(models.Model):

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(Manager, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"CreditRequest: {self.client.user.email} - {self.amount} - {self.status}"
    

