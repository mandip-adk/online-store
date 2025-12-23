from django.urls import path 
from . import views
app_name = "accounts"

urlpatterns =[
    path("register/",views.register_view , name="register_page"),
    path("login/",views.login_view , name="login_page"),
    path("home/",views.home_view , name="home_page"),
    path("logout/",views.logout_view , name="logout_page"),
]
