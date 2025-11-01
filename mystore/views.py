from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, Cart
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, ProfileUpdateForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRIT_KEY

# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required
def product_detail(request):
    products= Product.objects.all()
    return render(request, 'products.html', {'products': products})

def register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user) 
        return redirect('products')
    return render(request, 'register.html', {'form': form})
           
def login_view(request):
    form= AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and  form.is_valid():
        user= form.get_user()
        login(request, user)
        return redirect('products')
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_update(request):
    form= ProfileUpdateForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('products')
    return render(request, 'profile_update.html', {'forms': form})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart.quantity += 1
        cart.save()
    return redirect('cartview')
    
@login_required
def cart_view(requst):
    cart_item= Cart.objects.filter(user=requst.user)
    return render(requst, 'cart.html',{'cart':cart_item})

def remove_from_cart(request, product_id):
    Cart.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('cartview')

def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect('cartview')

@login_required
def checkout_single(request, product_id):
    product = get_object_or_404(Product, id=product_id)

        # ✅ Get quantity from cart (if added multiple times)
    cart_item = Cart.objects.get(user=request.user, product=product)
    quantity = cart_item.quantity
    
    total_price = product.price * quantity

    if request.method=='POST':
        checkout_session=stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    "price_data": {
                        "currency":"usd",
                        "product_data":{
                            "name":product.name
                            },
                        "unit_amount":int(product.price*100),
                    },
                    "quantity":quantity,
                },

            ],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("payment_success")),
            cancel_url=request.build_absolute_uri(reverse("checkout_single", args=[product.id])),
        )
        request.session['purchased_product_id'] = product.id

        return redirect(checkout_session.url)
    return render(request, 'checkout_single.html',{"product":product,"quantity": quantity,
        "total_price": total_price})


@login_required
def payment_success(request):
    product_id = request.session.pop('purchased_product_id', None)

    if product_id:
        Cart.objects.filter(user=request.user, product_id=product_id).delete()

    return render(request, "payment_success.html")