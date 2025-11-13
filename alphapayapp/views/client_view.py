from django.shortcuts import render, redirect
from authentication.models.User import User as UserModel
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from alphapayapp.models.Client import Client
from alphapayapp.models.Transfer import Transfer
from alphapayapp.models.Manager import Manager
from alphapayapp.models.Management import Management

@login_required(login_url='login')
def dashboard_view(request):

    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    account = Client.objects.get(user=client_user)
    transfers = Transfer.objects.filter(sender=account) | Transfer.objects.filter(receiver=account)
    transfers = transfers.order_by('-timestamp')[:5]

    context = {
        'user': client_user,
        'account': account,
        'transactions': transfers,
    }

    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def transfer_view(request):

    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    account = Client.objects.get(user=client_user)

    context = {
        'user': client_user,
        'user_account': account,
    }

    if request.method == 'POST':
        from decimal import Decimal

        reciver_account_number = request.POST.get('reciver_account_number')
        reciver_account = Client.objects.filter(account_number=reciver_account_number).first()
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        print(f'Receiver: {reciver_account}, Amount: {amount}, Description: {description}')

        if reciver_account and amount and Decimal(amount) > 0 and account.balance >= Decimal(amount):

            account.balance -= Decimal(amount)
            reciver_account.balance += Decimal(amount)

            account.save()
            reciver_account.save()

            transfer_data = Transfer.objects.create(
                sender=account,
                receiver=reciver_account,
                amount=amount,
                description=description
            )

            return redirect('success', transfer_id=transfer_data.id)

        else:
            context['error'] = 'Dados inválidos ou saldo insuficiente.'
            return render(request, 'transfer.html', context)

        return redirect('dashboard')

    return render(request, 'transfer.html', context)

@login_required(login_url='login')
def transfer_success_view(request, transfer_id):

    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    account = Client.objects.get(user=client_user)
    transfer = Transfer.objects.get(id=transfer_id)

    context = {
        'user': client_user,
        'user_account': account,
        'transfer': transfer,
        'reciver_account': transfer.receiver.account_number,
        'reciver_name': transfer.receiver.user.first_name + ' ' + transfer.receiver.user.last_name,
    }

    return render(request, 'success.html', context)

@login_required(login_url='login')
def profile_view(request):

    auth_user = request.user
    client_user = UserModel.objects.get(email=auth_user.email)
    account = Client.objects.get(user=client_user)

    context = {
        'user': client_user,
        'account': account,
    }

    return render(request, 'profile.html', context)