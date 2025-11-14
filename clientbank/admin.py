from django.contrib import admin
from clientbank.models.Client import Client
from clientbank.models.Transfer import Transfer

# Register your models here.

admin.site.register(Client)
admin.site.register(Transfer)


