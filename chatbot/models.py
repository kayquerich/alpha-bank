from django.db import models
from clientbank.models.Client import Client

# Create your models here.

class ChatMessage(models.Model):
    sender = models.CharField(max_length=50)  # 'user' or 'bot'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class ChatSession(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    messages = models.ManyToManyField(ChatMessage)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatSession for {self.client.user.email} at {self.created_at}"
