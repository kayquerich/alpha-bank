from django.shortcuts import render, redirect
from authentication.models.User import User as UserModel
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from clientbank.models.Client import Client
from management.models.Manager import Manager

# Create your views here.

def cadastro_view(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpf = request.POST.get('cpf')
        
        try: 
            user = UserModel.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                cpf=cpf
            )
            
            client = Client.objects.create(
                user=user,
                balance=0.00
            )
            
            print(f"Criado usuário {user.email} com conta número {client.account_number}")

            return redirect('login')
        except Exception as e:
            print(e)
            return render(request, 'cadastro.html', {'error': str(e)})

    return render(request, 'cadastro.html')

def login_view(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f'Email: {email}, Password: {password}')

        user = authenticate(request, username=email, password=password)
        print(user)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Email ou senha iválidos.'})
        
    return render(request, 'login.html')

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

@login_required(login_url='login')
def logout_view(request):

    is_manager = request.session.pop('is_manager', False)

    logout(request)

    if is_manager:
        return redirect('manager_login')
    return redirect('login')