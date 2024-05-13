import os
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from backend.models import (User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem,
                            Contact, ConfirmEmailToken, Import_file)
from backend.tasks import do_import


class UserInline(admin.TabularInline):
    model = User
    extra = 0


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class ContactInline(admin.StackedInline):
    model = Contact
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    inlines = [ContactInline,]
    list_display = ("email", "first_name", "last_name", "is_staff", "is_superuser", "is_active")
    model = User
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type', 'first_name', 'last_name', 'company', 'position')}),
        ('Permissions2', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
        }),

    )


# class ShopResource(resources.ModelResource):
#
#     class Meta:
#         model = Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    # resource_classes = [ShopResource]
    list_display = ("name", "url", "user", "state")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "url", "user", "state"),
            },
        ),
    )

    fieldsets = (
        (None, {'fields': ('name', 'url', 'user', 'state')}),
    )



# class ShopsInline(admin.TabularInline):
#     model = Category.shops.through
#     extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "shops"),
            },
        ),
    )

    fieldsets = (
        (None, {'fields': ("name", "shops")}),
    )


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category",]
    inlines = [ProductInfoInline,]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "category"),
            },
        ),
    )

    fieldsets = (
        (None, {'fields': ("name", "category")}),
    )


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 0


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ["model", "external_id", "product", "shop", "quantity", "price", "price_rrc",]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("model", "external_id", "product", "shop", "quantity", "price", "price_rrc",),
            },
        ),
    )

    fieldsets = (
        (None, {'fields': ("model", "external_id", "product", "shop", "quantity", "price", "price_rrc",)}),
    )
    inlines = [ProductParameterInline,]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["__str__", "dt", "user", "state",]
    readonly_fields = ["dt",]
    date_hierarchy = 'dt'
    inlines = [OrderItemInline,]
    fieldsets = (
        ("Some options", {
            'fields': ('user', 'state')
        }),
        ('Date options', {
            'classes': ('collapse',),
            'fields': ('dt',),
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product_info", "quantity",]
    readonly_fields = ["order",]
    # inlines = (ShopsInline,)




@admin.register(Import_file)
class PartnerImportAdmin(admin.ModelAdmin):
    list_display = ["yaml_file", "status", "date_added",]
    readonly_fields = ["status",]
    actions = ['export_selected_objects',]

    def delete_queryset(self, request, queryset):
        name_file = queryset.values_list('yaml_file', flat=True)[0]
        os.remove(name_file)
        queryset.delete()


    @admin.action(description='Загрузить тавары')
    def export_selected_objects(modeladmin, request, queryset):
        selected = queryset.values_list('id', flat=True)
        for id in selected:
           do_import.delay(file_id=id, user=request.user.id)



@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'created_at',]
