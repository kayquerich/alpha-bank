from django.contrib import admin
from clientbank.models.Client import Client
from clientbank.models.Transfer import Transfer
from clientbank.models.CreditRequest import CreditRequest
from clientbank.models.Credit import Credit
from clientbank.models.Invoice import Invoice

# Register your models here.

admin.site.register(Client)
admin.site.register(Transfer)
admin.site.register(CreditRequest)
admin.site.register(Credit)
admin.site.register(Invoice)


