from django.db import models
import random
from authentication.models.User import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from clientbank.models.Credit import Credit

class Client(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=254)
    phone_number = models.CharField(max_length=15)
    account_number = models.CharField(max_length=5, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    last_att = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if self._state.adding and not self.account_number:
            self.account_number = str(random.randint(10000, 99999))

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Client_Account: {self.user.email} - {self.user.cpf}"
    
@receiver(post_save, sender=Client)
def associate_manager (sender, instance, created, **kwargs):

    from management.models.Manager import Manager
    from management.models.Management import Management

    if created:

        managers = list(Manager.objects.all())
        
        if managers:
            random_manager = random.choice(managers)
            
            Management.objects.create(
                manager=random_manager,
                client=instance
            )

@receiver(post_save, sender=User)
def create_client_credit(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(user=instance)
        Credit.objects.create(client=instance.client_set.first())