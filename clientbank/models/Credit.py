from django.db import models

class Credit(models.Model):

    client = models.ForeignKey("clientbank.Client", on_delete=models.CASCADE)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Credit informations: {self.credit_limit} - {self.client.user.email}"