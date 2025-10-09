from django.db import models
from alphapayapp.models.Client import Client

class Transfer(models.Model):

    sender = models.ForeignKey(Client, related_name='sent_transfers', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Client, related_name='received_transfers', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transfer of {self.amount} from {self.sender} to {self.receiver} on {self.timestamp}'