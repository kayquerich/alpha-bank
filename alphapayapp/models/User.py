from django.db import models
from django.contrib.auth.hashers import make_password
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User as DjangoUser

class User(models.Model):

    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254)
    cpf = models.CharField(max_length=14, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    def save(self, *args, **kwargs):

        if not self.password:
            raise ValueError("Password cannot be empty.")
        
        if self.email:
            self.email = self.email.lower()

        if self.password:
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_auth_user(sender, instance, created, **kwargs):    
    if created:
        django_user = DjangoUser.objects.create_user(
            username=instance.email,
            email=instance.email,
        )
        django_user.password = instance.password
        django_user.save()