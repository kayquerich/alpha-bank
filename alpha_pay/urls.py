from django.contrib import admin
from django.urls import path
from alphapayapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test_view, name='test'),
    path('cadastro/', cadastro_view, name='cadastro'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('transfer/', transfer_view, name='transfer'),
    path('success/<int:transfer_id>/', transfer_success_view, name='success'),
    path('profile/', profile_view, name='profile'),
    path('managerlogin/', manage_login_view, name='managerlogin'),
]
