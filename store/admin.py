from django.contrib import admin
from .models import Product, Category, Cart, CartProduct , Payment, Order
from store.forms import OrderChangeForm

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Payment)

#admin.site.register(order)

@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ["order_id","status","user","total","created_at"]

    list_filter = ["status","delivery_person"]
    search_fields = ["order_id","user_email","user_first_name","user_last_name","delivery_person"]

    form = OrderChangeForm

    #disable delete
    def has_delete_permission(self, request, obj = ...):
        return False
    
    #disable add
    def has_add_permission(self, request):
        return False
    
