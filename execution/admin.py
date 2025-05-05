from django.contrib import admin
from django.utils.html import format_html
from .models import Job
from provider_services.models import Order


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ('id', 'title', 'customer', 'status', 'total_price')
    readonly_fields = ('id', 'title', 'customer', 'total_price')
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'job_name', 'service_provider', 'state', 'job_type', 'starting_date')
    list_filter = ('state', 'job_type', 'service_provider')
    search_fields = ('job_id', 'job_name')
    readonly_fields = ('completion_time',)
    date_hierarchy = 'starting_date'
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job_id', 'job_name', 'service_provider')
        }),
        ('Status', {
            'fields': ('state', 'job_type')
        }),
    )
    
    inlines = [OrderInline]