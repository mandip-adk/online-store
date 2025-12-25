from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartProduct
from django.core.paginator import Paginator
from .forms import ProductFilterForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField

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
    cart, created = Cart.objects.get_or_create(user=request.user)

    if CartProduct.objects.filter(product=product, cart=cart).exists():
        messages.info(request, "Product already in your cart")
        return redirect("store:product_detail_page", pk=pk)

    quantity = int(request.POST.get("quantity", 1))
    if quantity <= 0:
        messages.error(request, "Quantity must be at least 1")
        return redirect("store:product_detail_page", pk=pk)

    CartProduct.objects.create(
        product=product,
        cart=cart,
        quantity=quantity
    )

    messages.success(request, "Product added to cart successfully")
    return redirect("store:product_detail_page", pk=pk)

@login_required(login_url=reverse_lazy("accounts:login_page"))
def remove_from_cart(request, pk):
    try:
        cart_item = CartProduct.objects.get(pk=pk)
    except CartProduct.DoesNotExist:
        messages.error(request, "Cart item doesn't exists")

    except Exception as e:
        print(e)
        messages.error(request, "Removing item from cart failed")
    else:
        cart_item.delete()
        messages.success(request, "Cart item removed successfully")

    return redirect("store:cart_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def cart(request):
    try:
        user_cart = request.user.cart
        if user_cart is not None:
            #cart_products = CartProduct.objects.filter(cart=user_cart)
            #cart_total = 0
            #%for cart_item in cart_products:
                #cart_total += cart_item.get_total_price
            cart_products = CartProduct.objects.filter(cart=user_cart).annotate(
                subtotal=ExpressionWrapper(
                    F("product_price")*F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
            cart_total = cart_products.aaggregate(total=Sum("sumtotal"))["total"] or 0
            
    except Exception:
        messages.error(request ,"something went wrong, please try again later.")
        return redirect("store:home_page")
    
    context = {"products": cart_products, "cart_total": cart_total}

    return render(request, "store/cart.html", context)

@login_required(login_url=reverse_lazy("accounts:login_page"))
def update_cart(request, pk):
    if request.method == "POST":
        try:
            cart_product = CartProduct.objects.get(
                id=pk,
                cart=request.user.cart
            )

            quantity = int(request.POST.get("quantity", 1))
            cart_product.quantity = quantity
            cart_product.save()

        except CartProduct.DoesNotExist:
            messages.error(request, "Item not found in cart.")

    return redirect("store:cart_page")
