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

@login_required(login_url='login')
def dashboard_view(request):

    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    account = Client.objects.get(user=client_user)
    transfers = Transfer.objects.filter(sender=account) | Transfer.objects.filter(receiver=account)
    transfers = transfers.order_by('-timestamp')[:5]

    # Buscar informações de crédito e fatura
    credit = Credit.objects.filter(client=account).first()
    current_invoice = Invoice.objects.filter(
        client=account,
    ).order_by('-expiration_date').first()

    if current_invoice and current_invoice.pay:
        current_invoice = None


    # Calcular limite disponível
    available_limit = 0
    usage_percentage = 0
    usage_percentage_int = 0
    expiration_date_formatted = None

    if credit:
        invoice_value = current_invoice.value if current_invoice else 0
        available_limit = credit.credit_limit - invoice_value
        if credit.credit_limit > 0:
            usage_percentage = (invoice_value / credit.credit_limit) * 100
            usage_percentage_int = int(usage_percentage)
        if current_invoice:
            expiration_date_formatted = current_invoice.expiration_date.strftime("%d/%m/%Y")

    context = {
        'user': client_user,
        'account': account,
        'transactions': transfers,
        'credit': credit,
        'current_invoice': current_invoice,
        'available_limit': available_limit,
        'usage_percentage': usage_percentage_int,
        'expiration_date_formatted': expiration_date_formatted,
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

        reciver_account_number = request.POST.get('reciver_account_number')
        reciver_account = Client.objects.filter(account_number=reciver_account_number).first()
        amount = request.POST.get('amount')
        type = request.POST.get('payment_type')
        description = request.POST.get('description')

        print(f'Receiver: {reciver_account}, Amount: {amount}, Description: {description}')

        if reciver_account and amount and Decimal(amount) > 0 and account.balance >= Decimal(amount):
            if type == 'saldo':

                account.balance -= Decimal(amount)
                reciver_account.balance += Decimal(amount)

                account.save()
                reciver_account.save()

            elif type == 'credito':

                credit = Credit.objects.filter(client=account).first()
                actual_invoice = Invoice.objects.filter(
                    client=account,
                ).order_by('-expiration_date').first()

                if timezone.now().date().day >= 18 and actual_invoice and not actual_invoice.closed:
                    actual_invoice.closed = True
                    actual_invoice.closed_at = timezone.now()
                    actual_invoice.save()

                if actual_invoice and actual_invoice.closed:

                    if actual_invoice.expiration_date.month == 12:
                        new_year = actual_invoice.expiration_date.year + 1
                        new_month = 1
                    else:
                        new_year = actual_invoice.expiration_date.year
                        new_month = actual_invoice.expiration_date.month + 1

                    actual_invoice = Invoice.objects.create(
                        client=account,
                        value=Decimal('0.00'),
                        expiration_date=timezone.datetime(new_year, new_month, 25).date()
                    )

                invoices_list = Invoice.objects.filter(client=account, pay=False)
                total_invoices = sum(invoice.value for invoice in invoices_list)

                left_limit = credit.credit_limit - total_invoices

                if left_limit >= Decimal(amount):
                    actual_invoice.value += Decimal(amount)
                    actual_invoice.save()

                    reciver_account.balance += Decimal(amount)
                    reciver_account.save()
                else:
                    context['error'] = 'Limite de crédito insuficiente.'
                    return render(request, 'transfer.html', context)

            transfer_data = Transfer.objects.create(
                sender=account,
                receiver=reciver_account,
                amount=amount,
                type=type,
                description=description
            )

            return redirect('success', transfer_id=transfer_data.id)

        else:
            context['error'] = 'Dados inválidos ou saldo insuficiente.'
            return render(request, 'transfer.html', context)

        return redirect('dashboard')

    return render(request, 'transfer.html', context)

@login_required(login_url='login')
def deposit_view(request):
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    account = Client.objects.get(user=client_user)

    context = {
        'user': client_user,
        'user_account': account,
    }

    if request.method == 'POST':

        amount = request.POST.get('amount')

        print(f'Amount: {amount}')

        if amount and Decimal(amount) > 0:

            account.balance += Decimal(amount)

            account.save()

            # Here you might want to log the deposit as a transaction if needed

            return redirect('dashboard')

        else:
            context['error'] = 'Valor inválido para depósito.'
            return render(request, 'deposit.html', context)

    return render(request, 'deposit.html', context)

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

@login_required(login_url='login')
def credit_view(request):
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    account = Client.objects.get(user=client_user)
    actual_date = timezone.now().date() 
    
    # Buscar informações de crédito
    credit = Credit.objects.filter(client=account).first()
    
    # Buscar todas as faturas do cliente
    invoices = Invoice.objects.filter(client=account).order_by('-expiration_date')

    actual_invoice = Invoice.objects.filter(
        client=account,
    ).order_by('-expiration_date').first()
    
    # Calcular limite disponível
    available_limit = 0
    total_invoices = 0
    
    if credit:
        total_invoices = sum(invoice.value for invoice in invoices.filter(expiration_date__gte=actual_date, pay=False))
        available_limit = credit.credit_limit - total_invoices
    
    if actual_date.day >= 18 and actual_invoice and not actual_invoice.closed and not actual_invoice.pay and actual_date.month == actual_invoice.expiration_date.month and actual_date.year == actual_invoice.expiration_date.year:
        actual_invoice = invoices.filter(expiration_date__gte=actual_date).order_by('expiration_date').first()

        actual_invoice.closed = True
        actual_invoice.closed_at = timezone.now()
        actual_invoice.save()

    if request.method == 'POST':

        if actual_invoice and actual_invoice.closed:
            # Processar pagamento da fatura
            if account.balance >= actual_invoice.value:
                account.balance -= actual_invoice.value
                account.save()

                actual_invoice.pay = True
                actual_invoice.save()

                return redirect('credit')
        elif actual_invoice and not actual_invoice.closed:
            # Processar pagamento da fatura em aberto
            if account.balance >= actual_invoice.value:
                account.balance -= actual_invoice.value
                account.save()

                actual_invoice.value = Decimal('0.00')
                actual_invoice.save()

                return redirect('credit')
            else:
                error_message = "Saldo insuficiente para pagar a fatura."
                context = {
                    'user': client_user,
                    'account': account,
                    'credit': credit,
                    'invoices': invoices,
                    'available_limit': available_limit,
                    'total_invoices': total_invoices,
                    'error': error_message,
                }
                return render(request, 'credit.html', context)

    # Verificar se há solicitação pendente
    from clientbank.models.CreditRequest import CreditRequest
    pending_request = CreditRequest.objects.filter(client=account, status='pending').first()
    
    context = {
        'user': client_user,
        'account': account,
        'credit': credit,
        'invoices': invoices,
        'available_limit': available_limit,
        'total_invoices': total_invoices,
        'pending_request': pending_request,
    }
    
    return render(request, 'credit.html', context)

@login_required(login_url='login')
def request_credit_view(request):
    if request.method == 'POST':
        from clientbank.models.CreditRequest import CreditRequest
        
        user = request.user
        client_user = UserModel.objects.get(email=user.email)
        account = Client.objects.get(user=client_user)
        
        amount = request.POST.get('amount')
        
        if amount and Decimal(amount) > 0:
            # Verificar se já existe solicitação pendente
            pending_request = CreditRequest.objects.filter(client=account, status='pending').first()
            
            if not pending_request:
                CreditRequest.objects.create(
                    client=account,
                    amount=Decimal(amount),
                    status='pending'
                )
        
        return redirect('credit')
    
    return redirect('credit')

@login_required(login_url='login')
def update_client_view(request):
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    account = Client.objects.get(user=client_user)

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        if first_name:
            client_user.first_name = first_name
        if last_name:
            client_user.last_name = last_name
        if email:
            client_user.email = email.lower()
        if address:
            account.address = address
        if phone_number:
            account.phone_number = phone_number

        account.save()
        client_user.save()

        return redirect('profile')

    context = {
        'user': client_user,
        'account': account,
    }

    return render(request, 'update_client.html', context)