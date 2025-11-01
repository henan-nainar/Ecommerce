from django.urls import path
from .import views

urlpatterns = [
    path('',views.home, name='home'),
    path('products/',views.product_detail, name='products'),
    path('register/',views.register, name='register'),
    path('login/',views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
    path('profile_update/',views.profile_update, name='profile'),

    path('add_to_cart/<int:product_id>', views.add_to_cart, name= 'addtocart'),
    path('cart_view',views.cart_view, name='cartview'),
    path('remove_from_cart/<int:product_id>',views.remove_from_cart, name='removefromcart'),
    path('clear_cart/',views.clear_cart, name='clearcart'),
    path('checkout_single/<int:product_id>', views.checkout_single, name='checkout_single'),
    path("payment-success/", views.payment_success, name="payment_success"),


]