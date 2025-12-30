from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DeliveryPerson
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(CustomUser)
class CustomUserModelAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ("email","first_name","last_name",)
    ordering = ("email",)

    # 🔹 FIX change-user page
    fieldsets = (
        (None,
          {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    # 🔹 FIX add-user page
    add_fieldsets = (
        ("User Credentials",
            
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2",),
            },
        ),
        (
            "User Information",
            {
                "fields":("first_name","last_name","role"),
            },
        ),
    )

# admin.site.register(DeliveryPerson)
@admin.register(DeliveryPerson)
class DeliveryPersonModelAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number","dob","is_verified", "approved_at",)

    search_fields = ("user__email", "user__first_name", "user__last_name","phone_number",)

    list_filter = ("vehicle_color","is_verified")

    fieldsets = (
        ("basic Information", {"fields":("user","dob",)}),
        ("Contact Information", {"fields":("phone_number","emergency_contact",)}),
        ("Documents", {"fields":("citizenship","driving_license",)}),
        ("Vehicles Informations", {"fields":("vehicle_type","vehicle_plate_number","vehicle_color",)}),
        ("Account Information", {"fields":("is_active","is_verified",)}),
    )