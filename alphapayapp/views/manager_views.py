from django.shortcuts import render
from authentication.models.User import User as UserModel
from alphapayapp.models.Manager import Manager
from alphapayapp.models.Management import Management

def manager_dashboard_view(request):

    auth_user = request.user
    manager_user = UserModel.objects.get(email=auth_user.email)
    manager = Manager.objects.get(user=manager_user)
    managements = Management.objects.filter(manager=manager).select_related('client__user')

    context = {
        'manager': manager,
        'managements': managements,
    }

    return render(request, 'manager_dashboard.html', context)