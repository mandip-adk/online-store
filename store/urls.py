from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home_page"),
    path("products/", views.products, name="products_page"),
]
