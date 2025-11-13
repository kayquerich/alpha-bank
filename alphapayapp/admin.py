from django.contrib import admin
from alphapayapp.models.User import User
from alphapayapp.models.Client import Client
from alphapayapp.models.Manager import Manager
from alphapayapp.models.Management import Management
from alphapayapp.models.Transfer import Transfer

# Register your models here.

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Manager)
admin.site.register(Transfer)
admin.site.register(Management)