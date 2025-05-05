from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Report, JobReportResult, OrderReportResult, UserReportResult


class JobReportResultInline(admin.StackedInline):
    model = JobReportResult
    can_delete = False
    verbose_name_plural = 'Job Statistics'
    readonly_fields = (
        'total_jobs', 'avg_completion_time_regular', 'avg_completion_time_wafer_run',
        'jobs_created', 'jobs_active', 'jobs_completed', 'jobs_failed', 'jobs_delayed'
    )
    
    def has_add_permission(self, request, obj=None):
        return False


class OrderReportResultInline(admin.StackedInline):
    model = OrderReportResult
    can_delete = False
    verbose_name_plural = 'Order Statistics'
    readonly_fields = (
        'total_orders', 'total_revenue', 'average_order_value',
        'orders_draft', 'orders_submitted', 'orders_in_progress', 
        'orders_completed', 'orders_cancelled', 'avg_processing_time'
    )
    
    def has_add_permission(self, request, obj=None):
        return False


class UserReportResultInline(admin.StackedInline):
    model = UserReportResult
    can_delete = False
    verbose_name_plural = 'User Activity Statistics'
    readonly_fields = (
        'total_active_users', 'new_customers', 'active_account_managers',
        'top_performing_account_manager', 'top_customer', 
        'total_orders_by_top_manager', 'total_revenue_by_top_manager'
    )
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'report_type', 'time_period_display', 
        'created_by', 'created_at', 'has_pdf'
    )
    list_filter = ('report_type', 'year_from', 'year_to', 'quarter_from', 'quarter_to')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'description', 'report_type')
        }),
        ('Time Range', {
            'fields': (('quarter_from', 'year_from'), ('quarter_to', 'year_to'))
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'pdf_report')
        }),
    )
    inlines = [JobReportResultInline, OrderReportResultInline, UserReportResultInline]
    
    def time_period_display(self, obj):
        return f"{obj.quarter_from} {obj.year_from} - {obj.quarter_to} {obj.year_to}"
    time_period_display.short_description = "Time Period"
    
    def has_pdf(self, obj):
        if obj.pdf_report:
            return format_html(
                '<a href="{}" target="_blank">View PDF</a>',
                obj.pdf_report.url
            )
        return "No PDF"
    has_pdf.short_description = "PDF Report"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(JobReportResult)
class JobReportResultAdmin(admin.ModelAdmin):
    list_display = ('report_title', 'time_period', 'total_jobs', 'jobs_completed', 'jobs_active')
    list_filter = ('report__report_type', 'report__year_from', 'report__year_to')
    readonly_fields = (
        'report', 'total_jobs', 'avg_completion_time_regular', 'avg_completion_time_wafer_run',
        'jobs_created', 'jobs_active', 'jobs_completed', 'jobs_failed', 'jobs_delayed'
    )
    
    def report_title(self, obj):
        return obj.report.title
    report_title.short_description = "Report"
    
    def time_period(self, obj):
        return f"{obj.report.quarter_from} {obj.report.year_from} - {obj.report.quarter_to} {obj.report.year_to}"
    time_period.short_description = "Time Period"
    
    def has_add_permission(self, request):
        return False


@admin.register(OrderReportResult)
class OrderReportResultAdmin(admin.ModelAdmin):
    list_display = ('report_title', 'time_period', 'total_orders', 'total_revenue')
    list_filter = ('report__report_type', 'report__year_from', 'report__year_to')
    readonly_fields = (
        'report', 'total_orders', 'total_revenue', 'average_order_value',
        'orders_draft', 'orders_submitted', 'orders_in_progress', 
        'orders_completed', 'orders_cancelled', 'avg_processing_time'
    )
    
    def report_title(self, obj):
        return obj.report.title
    report_title.short_description = "Report"
    
    def time_period(self, obj):
        return f"{obj.report.quarter_from} {obj.report.year_from} - {obj.report.quarter_to} {obj.report.year_to}"
    time_period.short_description = "Time Period"
    
    def has_add_permission(self, request):
        return False


@admin.register(UserReportResult)
class UserReportResultAdmin(admin.ModelAdmin):
    list_display = ('report_title', 'time_period', 'total_active_users', 'new_customers', 'top_performers')
    list_filter = ('report__report_type', 'report__year_from', 'report__year_to')
    readonly_fields = (
        'report', 'total_active_users', 'new_customers', 'active_account_managers',
        'top_performing_account_manager', 'top_customer', 
        'total_orders_by_top_manager', 'total_revenue_by_top_manager'
    )
    
    def report_title(self, obj):
        return obj.report.title
    report_title.short_description = "Report"
    
    def time_period(self, obj):
        return f"{obj.report.quarter_from} {obj.report.year_from} - {obj.report.quarter_to} {obj.report.year_to}"
    time_period.short_description = "Time Period"
    
    def top_performers(self, obj):
        top_manager = obj.top_performing_account_manager
        top_customer = obj.top_customer
        
        manager_info = f"Manager: {top_manager}" if top_manager else "No top manager"
        customer_info = f"Customer: {top_customer}" if top_customer else "No top customer"
        
        return format_html("{} | {}", manager_info, customer_info)
    top_performers.short_description = "Top Performers"
    
    def has_add_permission(self, request):
        return False