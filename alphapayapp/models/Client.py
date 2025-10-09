from django.db import models
import random

class Client(models.Model):

    user = models.OneToOneField('alphapayapp.User', on_delete=models.CASCADE)
    address = models.CharField(max_length=254)
    phone_number = models.CharField(max_length=15)
    account_number = models.CharField(max_length=5, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if self._state.adding and not self.account_number:
            self.account_number = str(random.randint(10000, 99999))

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Client_Account: {self.user.email} - {self.user.cpf}"