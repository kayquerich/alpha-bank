from django.db import models
from alphapayapp.models.Client import Client
from alphapayapp.models.Manager import Manager

class Management (models.Model):

    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_att = models.DateTimeField(auto_now=True)

    def __str__(self):

        manager_name = self.manager.user.first_name + " " + self.manager.user.last_name
        client_name = self.client.user.first_name + " " + self.client.user.last_name

        return f"Acompanhamento {manager_name} - {client_name}"
    
    