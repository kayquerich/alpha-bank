from django.shortcuts import render, redirect
import alphapayapp.models.User as UserModel
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from alphapayapp.models.Client import Client
from alphapayapp.models.Transfer import Transfer
from alphapayapp.models.Manager import Manager
from alphapayapp.models.Management import Management

def manage_login_view(request): 

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')
        security_code = request.POST.get('security_code')
        
        print('chegou aqui')
        user = authenticate(request, username=email, password=password)
        print('passou por aqui')

        if user is not None:
            manager = Manager.objects.filter(security_code=security_code).first()
            if manager:
                login(request, user)
                # marca sessão para indicar login gerencial
                request.session['is_manager'] = True
                request.session['manager_id'] = manager.id
                print(f"Manager {email} logged in.")

                if not manager.user.email == email:
                    return render(request, 'manager_login.html', {'error' : 'Credênciais Inválidas.'})

                return redirect('manager_dashboard')
            else:
                return render(request, 'manager_login.html', {'error': 'Código de segurança inválido.'})

    return render(request, 'manager_login.html')

def manager_dashboard_view(request):

    auth_user = request.user
    manager_user = UserModel.User.objects.get(email=auth_user.email)
    manager = Manager.objects.get(user=manager_user)
    managements = Management.objects.filter(manager=manager).select_related('client__user')

    context = {
        'manager': manager,
        'managements': managements,
    }

    return render(request, 'manager_dashboard.html', context)