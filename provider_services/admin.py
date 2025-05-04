from django.contrib import admin
from .models import ServiceProvider, AccountManager, Customer, Service, Order, OrderItem


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(AccountManager)
class AccountManagerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'is_active')
    list_filter = ('is_active',)
    filter_horizontal = ('service_providers',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'created_at')
    filter_horizontal = ('account_managers',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_provider', 'price', 'is_active')
    list_filter = ('service_provider', 'is_active')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'account_manager', 'status', 'total_price')
    list_filter = ('status', 'account_manager')
    inlines = [OrderItemInline]
    readonly_fields = ('total_price',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is not superuser and belongs to account_manager group, 
        # only show orders they manage
        if not request.user.is_superuser and request.user.groups.filter(name='account_manager').exists():
            try:
                account_manager = AccountManager.objects.get(user=request.user)
                return qs.filter(account_manager=account_manager)
            except AccountManager.DoesNotExist:
                return qs.none()
        return qs