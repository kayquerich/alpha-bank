from django.contrib import admin
from alphapayapp.models.User import User
from alphapayapp.models.Client import Client
from alphapayapp.models.Manager import Manager

# Register your models here.

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Manager)