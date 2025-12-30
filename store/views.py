from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartProduct , Order , OrderItem, Payment
from django.core.paginator import Paginator
from .forms import ProductFilterForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from .utils import generate_order_id
from django.db import transaction, IntegrityError
import requests
import json
from decimal import Decimal
from django.conf import settings


def home(request):

    featured_products = Product.objects.filter(featured=True).order_by("-created_at")[
        :8
    ]

    context = {"products": featured_products}

    return render(request, "store/home.html", context)


def products(request):
    products = Product.objects.all()

    filter_form = ProductFilterForm(request.GET)
    
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('name'):
            products = products.filter(
                name__icontains=filter_form.cleaned_data.get('name')
            )

        if filter_form.cleaned_data.get('min_price'):
            products = products.filter(
                price__gte=filter_form.cleaned_data.get('min_price')
            )

        if filter_form.cleaned_data.get('max_price'):
                products = products.filter(
                price__lte=filter_form.cleaned_data.get('max_price')
            )

        if filter_form.cleaned_data.get('categories'):
                products = products.filter(
                categories__in=filter_form.cleaned_data.get('categories')
            )
    
        sorting_key= filter_form.cleaned_data.get("sorting_key")
        if sorting_key=="price_asc":
             products = products.order_by("price")
        elif sorting_key=="price_desc":
             products = products.order_by("-price")
        elif sorting_key=="oldest":
             products = products.order_by("created_at")
        elif sorting_key=="latest":
             products = products.order_by("-created_at")

    products_paginator = Paginator(products, 16)
    page_number = request.GET.get("page")
    page_obj = products_paginator.get_page(page_number)

    

    context = {"products": page_obj,"filter_form": filter_form, }
    return render(request, "store/products.html", context)

def product_detail(request, pk):
     
    product = get_object_or_404(Product, pk=pk)
    context = {"product":product}
    return render(request,"store/product_detail.html", context) 

@login_required(login_url=reverse_lazy("accounts:login_page"))
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_product, created = CartProduct.objects.get_or_create(
        product=product,
        cart=cart,
        defaults={"quantity": int(request.POST.get("quantity", 1))}
    )

    if not created:
        cart_product.quantity += int(request.POST.get("quantity", 1))
        cart_product.save()
        messages.info(request, "Product quantity updated in cart")
    else:
        messages.success(request, "Product added to cart successfully")

    return redirect("store:product_detail_page", pk=pk)


@login_required(login_url=reverse_lazy("accounts:login_page"))
def remove_from_cart(request, pk):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect("store:cart_page")

    try:
        cart_item = CartProduct.objects.get(pk=pk, cart=cart)
        cart_item.delete()
        messages.success(request, "Cart item removed successfully")
    except CartProduct.DoesNotExist:
        messages.error(request, "Cart item not found")

    return redirect("store:cart_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_products = CartProduct.objects.filter(cart=cart).annotate(
        subtotal=ExpressionWrapper(
            F("product__price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )

    cart_total = cart_products.aggregate(
        total=Sum("subtotal")
    )["total"] or 0

    context = {
        "products": cart_products,
        "cart_total": cart_total
    }

    return render(request, "store/cart.html", context)


@login_required(login_url=reverse_lazy("accounts:login_page"))
def update_cart(request, pk):
    if request.method == "POST":
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return redirect("store:cart_page")

        try:
            cart_product = CartProduct.objects.get(pk=pk, cart=cart)
            quantity = int(request.POST.get("quantity", 1))

            if quantity >= 1:
                cart_product.quantity = quantity
                cart_product.save()
            else:
                messages.error(request, "Quantity must be at least 1")

        except CartProduct.DoesNotExist:
            messages.error(request, "Item not found in cart")

    return redirect("store:cart_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def place_order(request):
    user_cart = request.user.cart

    cart_products = CartProduct.objects.filter(cart=user_cart).annotate(
        subtotal=ExpressionWrapper(
            F("product__price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )
    cart_sub_total = cart_products.aggregate(total=Sum("subtotal"))["total"] or 0

    try:
        order_id = generate_order_id(request.user.id)
        with transaction.atomic():
            # create new order
            new_order = Order.objects.create(
                user=request.user, order_id=order_id,
                subtotal=cart_sub_total,
                total = cart_sub_total,
            )

            # create order items for newly created order
            for cart_item in cart_products:
                OrderItem.objects.create(
                    order=new_order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )

            # remove ordered items from cart
            for cart_item in cart_products:
                cart_item.delete()

    except IntegrityError:
        messages.error(request, "Failed to create an order")
        return redirect("store:cart_page")
    except Exception as e:
        print("Unexpected behaviour: ", str(e))
        return redirect("store:cart_page")
    else:
        messages.success(request, "Order placed successful")
        return redirect("store:order_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def cancel_order(request, pk):
    try:
        order_to_delete = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        messages.error(request, "Failed to cancel the order")
    else:
        order_to_delete.delete()
        messages.success(request, "Order cancel successful")

    return redirect("store:order_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def order(request):

    orders = Order.objects.filter(user=request.user)

    context = {"orders": orders}

    return render(request, "store/order.html", context)


@login_required(login_url="accounts:login_page")
def khalti_payment(request, order_id):
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user,
    )

    if order.status == Order.Status.PAID:
        messages.info(request, "This order is already paid.")
        return redirect("store:order_page")
    
    purchase_order_id = f"TR-{order.order_id}"

    # 2. Create or reuse payment safely
    payment, created = Payment.objects.get_or_create(
        purchase_order_id=purchase_order_id,
        defaults={
            "order": order,
            "amount": order.total,
            "status": Payment.Status.INITIATED,
        },
    )

    if not created and payment.status != Payment.Status.INITIATED:
        messages.warning(request, "Payment already processed for this order.")
        return redirect("store:order_page")

    amount_paisa = int((payment.amount * Decimal("100")).quantize(Decimal("1")))

    payload = {
        "return_url": settings.SITE_URL + reverse("store:khalti_payment_response"),
        "website_url": settings.SITE_URL + reverse("store:home_page"),
        "amount": amount_paisa,
        "purchase_order_id": payment.purchase_order_id,
        "purchase_order_name": str(order.order_id),
        "customer_info": {
            "name": request.user.get_full_name() or request.user.email,
            "email": request.user.email,
            "phone": getattr(order, "phone", "no phone"),
        },
    }
    if not created and payment.status != Payment.Status.INITIATED:
        messages.warning(request, "Payment already processed for this order.")
        return redirect("store:order_page")

    amount_paisa = int((payment.amount * Decimal("100")).quantize(Decimal("1")))

    payload = {
        "return_url": settings.SITE_URL + reverse("store:khalti_payment_response"),
        "website_url": settings.SITE_URL + reverse("store:home_page"),
        "amount": amount_paisa,
        "purchase_order_id": payment.purchase_order_id,
        "purchase_order_name": str(order.order_id),
        "customer_info": {
            "name": request.user.get_full_name() or request.user.email,
            "email": request.user.email,
            "phone": getattr(order, "phone", "no phone"),
        },
    }

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://dev.khalti.com/api/v2/epayment/initiate/",
            json=payload,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        messages.error(request, "Payment service unavailable. Try again later.")
        return redirect("store:order_page")
    pidx = data.get("pidx")
    payment_url = data.get("payment_url")

    if not pidx or not payment_url:
        messages.error(request, "Invalid response from payment gateway.")
        return redirect("store:order_page")
    
    payment.pidx = pidx
    payment.save(update_fields=["pidx"])

    return redirect(payment_url)




@login_required(login_url=reverse_lazy("accounts:login_page"))
def khalti_payment_response(request):
    payment_status = request.GET.get("status")
    pidx = request.GET.get("pidx")
    transaction_id = request.GET.get("transcation_id")
    purchase_order_id = request.GET.get("purchase_order_id")
    amount =Decimal (request.Get.get("total_amount")) /100


    try:
        payment = Payment.objects.get(
            pidx=pidx,
            purchase_order_id=purchase_order_id,
            amount=amount
        )
    except Payment.DoesNotExist:
        messages.error(request, "Payment not verified yet, please contact the administrator.")
        return redirect("store:home_page")
    except Exception:
        messages.error(request, "Payment not verified yet, please contact the administrator.")
        return redirect("store:home_page")
    else:
        try:
            with transaction.atomic():
                payment.status = Payment.Status.SUCCESS
                payment.save()
                
                order = payment.order   # ✅ get related order object
                order.status = Order.Status.PAID
                order.save()

        except IntegrityError:
            messages.error(request, "Payment not verified yet, please contact the administrator.")
            return redirect("store:home_page")
        else:
            messages.success(
                request,
                "Payment done, please wait for product to reach your doorstep."
            )
            return redirect("store:order_page")
