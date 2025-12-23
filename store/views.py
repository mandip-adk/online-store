from django.shortcuts import render
from .models import Product
from django.core.paginator import Paginator


def home(request):

    featured_products = Product.objects.filter(featured=True).order_by("-created_at")[
        :8
    ]

    context = {"products": featured_products}

    return render(request, "store/home.html", context)


def products(request):

    products = Product.objects.all().order_by("-created_at")
    products_paginator = Paginator(products, 16)
    page_number = request.GET.get("page")
    page_obj = products_paginator.get_page(page_number)

    context = {"products": page_obj}
    return render(request, "store/products.html", context)