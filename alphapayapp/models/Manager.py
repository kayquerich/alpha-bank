from django.db import models
import random

class Manager(models.Model):

    user = models.OneToOneField('alphapayapp.User', on_delete=models.CASCADE)
    security_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_att = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if self._state.adding and not self.security_code:
            self.security_code = str(random.randint(100000, 999999))

        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Manager: {self.user.email} - Code: {self.security_code}"
    
