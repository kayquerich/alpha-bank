from django.contrib import admin
from django.urls import path
from management.views import *
from authentication.views import *
from clientbank.views import *
from chatbot.views import *
from ecommerce.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test_view, name='test'),
    path('cadastro/', cadastro_view, name='cadastro'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('transfer/', transfer_view, name='transfer'),
    path('deposit/', deposit_view, name='deposit'),
    path('success/<int:transfer_id>/', transfer_success_view, name='success'),
    path('profile/', profile_view, name='profile'),
    path('credit/', credit_view, name='credit'),
    path('credit/request/', request_credit_view, name='request_credit'),
    path('manager/login/', manage_login_view, name='manager_login'),
    path('manager/dashboard/', manager_dashboard_view, name='manager_dashboard'),
    path('manager/credit-requests/', credit_requests_view, name='credit_requests'),
    path('update-client/', update_client_view, name='update_client'),
    path('assistant/', assistant_view, name='assistant'),
    path('ecommerce/', home_view, name='ecommerce_home'),
]
