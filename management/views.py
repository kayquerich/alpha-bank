from django.shortcuts import render
from authentication.models.User import User as UserModel
from management.models.Manager import Manager
from management.models.Management import Management
from clientbank.models.CreditRequest import CreditRequest
from django.contrib.auth.decorators import login_required
from django import template

def get_credit_requests(manager, managements):

    credit_requests = []

    for management in managements:
        requests = CreditRequest.objects.filter(client=management.client, status='pending')
        credit_requests.extend(requests)
    
    return credit_requests
    
@login_required(login_url='manager_login')
def manager_dashboard_view(request):

    auth_user = request.user
    manager_user = UserModel.objects.get(email=auth_user.email)
    manager = Manager.objects.get(user=manager_user)
    managements = Management.objects.filter(manager=manager).select_related('client__user')
    

    context = {
        'manager': manager,
        'managements': managements,
        'credit_requests': get_credit_requests(manager, managements)
    }

    return render(request, 'manager_dashboard.html', context)

@login_required(login_url='manager_login')
def credit_requests_view(request):
    
    auth_user = request.user
    manager_user = UserModel.objects.get(email=auth_user.email)
    manager = Manager.objects.get(user=manager_user)
    managements = Management.objects.filter(manager=manager).select_related('client__user')

    if request.method == 'POST':
        from django.shortcuts import redirect
        from django.utils import timezone
        from clientbank.models.Credit import Credit
        
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        try:
            credit_request = CreditRequest.objects.get(id=request_id, status='pending')
            
            # Verificar se o gerente tem permissão para este cliente
            client_ids = [m.client.id for m in managements]
            if credit_request.client.id not in client_ids:
                return redirect('credit_requests')
            
            if action == 'approve':
                # Aprovar solicitação
                credit_request.status = 'approved'
                credit_request.reviewed_at = timezone.now()
                credit_request.reviewed_by = manager
                credit_request.notes = notes
                credit_request.save()
                
                # Adicionar ou atualizar crédito do cliente
                credit, created = Credit.objects.get_or_create(client=credit_request.client)
                credit.credit_limit += credit_request.amount
                credit.save()
                
            elif action == 'reject':
                # Rejeitar solicitação
                credit_request.status = 'rejected'
                credit_request.reviewed_at = timezone.now()
                credit_request.reviewed_by = manager
                credit_request.notes = notes
                credit_request.save()
        
        except CreditRequest.DoesNotExist:
            pass
        
        return redirect('credit_requests')

    credit_requests = get_credit_requests(manager, managements)

    context = {
        'manager': manager,
        'credit_requests': credit_requests
    }

    return render(request, 'credit_requests.html', context)

def test_view(request):

    context = {
        'message': 'This is a test view',
        'user' : 'Kayque',
        'range': range(0,10)
    }

    return render(request, 'test.html', context)

register = template.Library()

@register.filter
def request_aprove(idRequest):
    try:
        credit_request = CreditRequest.objects.get(id=idRequest)
        credit_request.status = 'approved'
        credit_request.save()

        client = credit_request.client

        from clientbank.models.Credit import Credit

        credit = Credit.objects.get_or_create(client=client)[0]
        credit.amount += credit_request.amount
        credit.save()

        return True
    except CreditRequest.DoesNotExist:
        return False