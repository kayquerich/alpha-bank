from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from ecommerce.models.Product import Product
from ecommerce.models.Cart import Cart
from ecommerce.models.CartItem import CartItem
from ecommerce.models.Order import Order
from ecommerce.models.OrderItem import OrderItem
from clientbank.models.Client import Client
from authentication.models.User import User as UserModel

# Create your views here.

@login_required(login_url='login')
def home_view(request):

    products = Product.objects.all()
    
    # Busca o carrinho para mostrar contador no header
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    cart = Cart.objects.filter(client=client).first()
    items_count = cart.items.count() if cart else 0

    context = {
        'products': products,
        'items_count': items_count
    }

    return render(request, 'home.html', context)

@login_required(login_url='login')
def product_detail_view(request, product_id):

    product = Product.objects.get(id=product_id)
    
    # Busca o carrinho para mostrar contador no header
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    cart = Cart.objects.filter(client=client).first()
    items_count = cart.items.count() if cart else 0

    return render(request, 'details.html', {
        'product': product,
        'items_count': items_count
    })

@login_required(login_url='login')
def cart_view(request):
    
    # Busca o usuário customizado pelo email do request.user
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    # Busca ou cria o carrinho do cliente
    cart, created = Cart.objects.get_or_create(client=client)
    
    # Busca todos os itens do carrinho
    cart_items = cart.items.all().select_related('product')
    
    # Calcula o total
    total = sum(item.get_subtotal() for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'items_count': cart_items.count()
    }

    return render(request, 'cart.html', context)

@login_required(login_url='login')
def add_to_cart(request, product_id):
    
    if request.method != 'POST':
        return redirect('home')
    
    # Busca o produto
    product = get_object_or_404(Product, id=product_id)
    
    # Busca o cliente
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    # Busca ou cria o carrinho do cliente
    cart, created = Cart.objects.get_or_create(client=client)
    
    # Busca ou cria o item no carrinho
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    # Se o item já existia, aumenta a quantidade
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Quantidade de "{product.name}" atualizada no carrinho!')
    else:
        messages.success(request, f'"{product.name}" adicionado ao carrinho!')
    
    # Redireciona de volta para a página de detalhes do produto
    return redirect('product_detail', product_id=product_id)

@login_required(login_url='login')
def increase_cart_item(request, item_id):
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)
    
    # Busca o item
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Verifica se o item pertence ao carrinho do usuário
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    if cart_item.cart.client != client:
        return JsonResponse({'success': False, 'error': 'Acesso negado'}, status=403)
    
    # Aumenta a quantidade
    cart_item.quantity += 1
    cart_item.save()
    
    # Recalcula o total do carrinho
    cart_items = cart_item.cart.items.all()
    total = sum(item.get_subtotal() for item in cart_items)
    
    return JsonResponse({
        'success': True,
        'quantity': cart_item.quantity,
        'subtotal': float(cart_item.get_subtotal()),
        'total': float(total),
        'items_count': cart_items.count()
    })

@login_required(login_url='login')
def decrease_cart_item(request, item_id):
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)
    
    # Busca o item
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Verifica se o item pertence ao carrinho do usuário
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    if cart_item.cart.client != client:
        return JsonResponse({'success': False, 'error': 'Acesso negado'}, status=403)
    
    # Se quantidade for 1, remove o item
    if cart_item.quantity <= 1:
        product_name = cart_item.product.name
        cart = cart_item.cart
        cart_item.delete()
        
        # Recalcula o total do carrinho
        cart_items = cart.items.all()
        total = sum(item.get_subtotal() for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'removed': True,
            'total': float(total),
            'items_count': cart_items.count(),
            'message': f'"{product_name}" removido do carrinho'
        })
    
    # Diminui a quantidade
    cart_item.quantity -= 1
    cart_item.save()
    
    # Recalcula o total do carrinho
    cart_items = cart_item.cart.items.all()
    total = sum(item.get_subtotal() for item in cart_items)
    
    return JsonResponse({
        'success': True,
        'quantity': cart_item.quantity,
        'subtotal': float(cart_item.get_subtotal()),
        'total': float(total),
        'items_count': cart_items.count()
    })

@login_required(login_url='login')
def remove_cart_item(request, item_id):
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)
    
    # Busca o item
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Verifica se o item pertence ao carrinho do usuário
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    if cart_item.cart.client != client:
        return JsonResponse({'success': False, 'error': 'Acesso negado'}, status=403)
    
    product_name = cart_item.product.name
    cart = cart_item.cart
    cart_item.delete()
    
    # Recalcula o total do carrinho
    cart_items = cart.items.all()
    total = sum(item.get_subtotal() for item in cart_items)
    
    return JsonResponse({
        'success': True,
        'total': float(total),
        'items_count': cart_items.count(),
        'message': f'"{product_name}" removido do carrinho'
    })

@login_required(login_url='login')
def checkout_page(request):
    """Página de checkout com formulário de entrega"""
    
    # Busca o cliente
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    # Busca o carrinho
    cart = get_object_or_404(Cart, client=client)
    cart_items = cart.items.all()
    
    # Valida se há itens no carrinho
    if not cart_items.exists():
        messages.error(request, 'Seu carrinho está vazio!')
        return redirect('cart')
    
    # Calcula o total
    total = sum(item.get_subtotal() for item in cart_items)
    
    # Calcula o saldo após a compra
    saldo_atual = client.balance
    saldo_apos_compra = saldo_atual - total
    
    # Verifica se tem saldo suficiente
    saldo_suficiente = saldo_atual >= total
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'items_count': cart_items.count(),
        'saldo_atual': saldo_atual,
        'saldo_apos_compra': saldo_apos_compra,
        'saldo_suficiente': saldo_suficiente,
        'client': client,
    }
    
    return render(request, 'checkout.html', context)

@login_required(login_url='login')
@transaction.atomic
def checkout(request):
    
    if request.method != 'POST':
        return redirect('cart')
    
    # Busca o cliente
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    # Busca o carrinho
    cart = get_object_or_404(Cart, client=client)
    cart_items = cart.items.all()
    
    # Valida se há itens no carrinho
    if not cart_items.exists():
        messages.error(request, 'Seu carrinho está vazio!')
        return redirect('cart')
    
    # Calcula o total
    total = sum(item.get_subtotal() for item in cart_items)
    
    # Verifica se o cliente tem saldo suficiente
    if client.balance < total:
        messages.error(request, f'Saldo insuficiente! Você possui R$ {client.balance:.2f} e a compra total é R$ {total:.2f}.')
        return redirect('checkout_page')
    
    # Captura dados do formulário
    delivery_address = request.POST.get('delivery_address', '')
    delivery_number = request.POST.get('delivery_number', '')
    delivery_complement = request.POST.get('delivery_complement', '')
    delivery_city = request.POST.get('delivery_city', '')
    delivery_state = request.POST.get('delivery_state', '')
    delivery_zipcode = request.POST.get('delivery_zipcode', '')
    
    # Deduz o valor do saldo do cliente
    client.balance -= total
    client.save()
    
    # Cria o pedido
    order = Order.objects.create(
        client=client,
        total_amount=total,
        status='processing'
    )
    
    # Cria os itens do pedido (cópia dos itens do carrinho)
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_name=cart_item.product.name,
            product_price=cart_item.product.price,
            quantity=cart_item.quantity
        )
    
    # Limpa o carrinho
    cart_items.delete()
    
    messages.success(request, f'🎉 Compra finalizada com sucesso! Pedido #{order.order_number} | Valor: R$ {total:.2f} | Novo saldo: R$ {client.balance:.2f}')
    return redirect('order_detail', order_id=order.id)

@login_required(login_url='login')
def my_orders(request):
    
    # Busca o cliente
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    # Busca todos os pedidos do cliente
    orders = Order.objects.filter(client=client).prefetch_related('items__product')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'my_orders.html', context)

@login_required(login_url='login')
def order_detail(request, order_id):
    
    # Busca o cliente
    user = request.user
    client_user = UserModel.objects.get(email=user.email)
    client = Client.objects.get(user=client_user)
    
    # Busca o pedido
    order = get_object_or_404(Order, id=order_id, client=client)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'order_detail.html', context)