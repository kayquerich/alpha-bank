from django.shortcuts import render, redirect
from authentication.models.User import User as UserModel
from django.contrib.auth.decorators import login_required
from clientbank.models.Client import Client
from clientbank.models.Transfer import Transfer
from clientbank.models.Credit import Credit
from clientbank.models.Invoice import Invoice
from management.models.Manager import Manager
from management.models.Management import Management
from django.utils import timezone
from decimal import Decimal

# Create your views here.

@login_required(login_url='login')
def assistant_view(request):

    auth_user = request.user
    user = UserModel.objects.get(email=auth_user.email)
    client = Client.objects.get(user=user)

    context = {
        'client': client,
    }

    return render(request, 'interface.html', context)