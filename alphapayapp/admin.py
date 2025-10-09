from django.contrib import admin
from alphapayapp.models.User import User
from alphapayapp.models.Client import Client

# Register your models here.

admin.site.register(User)
admin.site.register(Client)