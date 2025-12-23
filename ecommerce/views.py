from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ecommerce.models.Product import Product

# Create your views here.

@login_required(login_url='login')
def home_view(request):

    products = Product.objects.all()

    context = {
        'products': products
    }

    return render(request, 'home.html', context)

@login_required(login_url='login')
def product_detail_view(request, product_id):

    product = Product.objects.get(id=product_id)

    return render(request, 'details.html', { 'product': product })