import datetime
from decimal import Decimal
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, fields
from django.db import models
from django.apps import apps
from django.contrib.auth.models import User

# Dynamic model imports to avoid circular imports
def get_model(app_label, model_name):
    return apps.get_model(app_label, model_name)


def calculate_report_statistics(report):
    """Main function to calculate all statistics for a report based on its type."""
    if report.report_type in ['job', 'combined']:
        calculate_job_statistics(report)
    
    if report.report_type in ['order', 'combined']:
        calculate_order_statistics(report)
        
    if report.report_type in ['user', 'combined']:
        calculate_user_statistics(report)


def get_quarter_dates(quarter, year):
    """Convert quarter and year to start and end dates."""
    if quarter == 'Q1':
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 3, 31)
    elif quarter == 'Q2':
        start_date = datetime.date(year, 4, 1)
        end_date = datetime.date(year, 6, 30)
    elif quarter == 'Q3':
        start_date = datetime.date(year, 7, 1)
        end_date = datetime.date(year, 9, 30)
    elif quarter == 'Q4':
        start_date = datetime.date(year, 10, 1)
        end_date = datetime.date(year, 12, 31)
    else:
        raise ValueError("Invalid quarter. Please use 'Q1', 'Q2', 'Q3', or 'Q4'.")
    return start_date, end_date


def get_date_range_for_report(report):
    """Get date range for a report based on quarters and years."""
    start_date_from, end_date_from = get_quarter_dates(report.quarter_from, report.year_from)
    start_date_to, end_date_to = get_quarter_dates(report.quarter_to, report.year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)
    
    return start_date, end_date


def calculate_job_statistics(report):
    """Calculate job statistics for the report's time range."""
    Job = get_model("execution", "Job")
    JobReportResult = get_model("stat_analysis", "JobReportResult")
    
    start_date, end_date = get_date_range_for_report(report)
    
    # Get all jobs in the time range
    jobs_in_period = Job.objects.filter(
        starting_date__gte=start_date,
        starting_date__lte=end_date
    )
    
    # Calculate total jobs
    total_jobs = jobs_in_period.count()
    
    # Calculate average completion time per job type
    completed_jobs = jobs_in_period.filter(state='completed')
    avg_completion_regular = completed_jobs.filter(job_type='regular').aggregate(
        avg=Avg('completion_time')
    )['avg'] or 0
    
    avg_completion_wafer_run = completed_jobs.filter(job_type='wafer_run').aggregate(
        avg=Avg('completion_time')
    )['avg'] or 0
    
    # Calculate jobs per status
    jobs_created = jobs_in_period.filter(state='created').count()
    jobs_active = jobs_in_period.filter(state='active').count()
    jobs_completed = jobs_in_period.filter(state='completed').count()
    jobs_failed = jobs_in_period.filter(state='failed').count()
    jobs_delayed = jobs_in_period.filter(state='delayed').count()
    
    # Get or create job report result
    job_result, created = JobReportResult.objects.get_or_create(
        report=report,
        defaults={
            'total_jobs': total_jobs,
            'avg_completion_time_regular': avg_completion_regular,
            'avg_completion_time_wafer_run': avg_completion_wafer_run,
            'jobs_created': jobs_created,
            'jobs_active': jobs_active,
            'jobs_completed': jobs_completed,
            'jobs_failed': jobs_failed,
            'jobs_delayed': jobs_delayed
        }
    )
    
    if not created:
        # Update existing report
        job_result.total_jobs = total_jobs
        job_result.avg_completion_time_regular = avg_completion_regular
        job_result.avg_completion_time_wafer_run = avg_completion_wafer_run
        job_result.jobs_created = jobs_created
        job_result.jobs_active = jobs_active
        job_result.jobs_completed = jobs_completed
        job_result.jobs_failed = jobs_failed
        job_result.jobs_delayed = jobs_delayed
        job_result.save()
    
    return job_result


def calculate_order_statistics(report):
    """Calculate order statistics for the report's time range."""
    Order = get_model("provider_services", "Order")
    OrderReportResult = get_model("stat_analysis", "OrderReportResult")
    
    start_date, end_date = get_date_range_for_report(report)
    
    # Get all orders in the time range
    orders_in_period = Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )
    
    # Calculate basic order statistics
    total_orders = orders_in_period.count()
    total_revenue = orders_in_period.aggregate(sum=Sum('total_price'))['sum'] or 0
    average_order_value = Decimal('0.00')
    if total_orders > 0:
        average_order_value = total_revenue / total_orders
    
    # Calculate orders per status
    orders_draft = orders_in_period.filter(status='draft').count()
    orders_submitted = orders_in_period.filter(status='submitted').count()
    orders_in_progress = orders_in_period.filter(status='in_progress').count()
    orders_completed = orders_in_period.filter(status='completed').count()
    orders_cancelled = orders_in_period.filter(status='cancelled').count()
    
    # Calculate average processing time (for completed orders)
    completed_orders = orders_in_period.filter(status='completed', completed_at__isnull=False)
    avg_processing_time = None
    if completed_orders.exists():
        # Calculate difference in days
        processing_time_expr = ExpressionWrapper(
            F('completed_at') - F('created_at'),
            output_field=fields.DurationField()
        )
        avg_time = completed_orders.annotate(
            processing_time=processing_time_expr
        ).aggregate(avg=Avg('processing_time'))['avg']
        
        if avg_time:
            avg_processing_time = avg_time.total_seconds() / (24 * 3600)  # Convert to days
    
    # Get or create order report result
    order_result, created = OrderReportResult.objects.get_or_create(
        report=report,
        defaults={
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': average_order_value,
            'orders_draft': orders_draft,
            'orders_submitted': orders_submitted,
            'orders_in_progress': orders_in_progress,
            'orders_completed': orders_completed,
            'orders_cancelled': orders_cancelled,
            'avg_processing_time': avg_processing_time
        }
    )
    
    if not created:
        # Update existing report
        order_result.total_orders = total_orders
        order_result.total_revenue = total_revenue
        order_result.average_order_value = average_order_value
        order_result.orders_draft = orders_draft
        order_result.orders_submitted = orders_submitted
        order_result.orders_in_progress = orders_in_progress
        order_result.orders_completed = orders_completed
        order_result.orders_cancelled = orders_cancelled
        order_result.avg_processing_time = avg_processing_time
        order_result.save()
    
    return order_result


def calculate_user_statistics(report):
    """Calculate user statistics for the report's time range."""
    User = get_model("auth", "User")
    Order = get_model("provider_services", "Order")
    UserReportResult = get_model("stat_analysis", "UserReportResult")
    AccountManager = get_model("provider_services", "AccountManager")
    Customer = get_model("provider_services", "Customer")
    
    start_date, end_date = get_date_range_for_report(report)
    
    # Get active users in the time range
    active_users = User.objects.filter(
        last_login__gte=start_date,
        last_login__lte=end_date
    )
    
    # Get new customers in the time range
    new_customers = Customer.objects.filter(
        user__date_joined__gte=start_date,
        user__date_joined__lte=end_date
    ).count()
    
    # Get active account managers 
    active_managers = AccountManager.objects.filter(
        user__in=active_users
    ).count()
    
    # Find top performing account manager based on orders
    top_manager = None
    top_manager_orders = 0
    top_manager_revenue = Decimal('0.00')
    
    managers = AccountManager.objects.all()
    for manager in managers:
        manager_orders = Order.objects.filter(
            account_manager=manager,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        order_count = manager_orders.count()
        revenue = manager_orders.aggregate(sum=Sum('total_price'))['sum'] or 0
        
        if order_count > top_manager_orders:
            top_manager = manager.user
            top_manager_orders = order_count
            top_manager_revenue = revenue
    
    # Find top customer based on orders
    top_customer = None
    customers = Customer.objects.all()
    top_customer_orders = 0
    
    for customer in customers:
        customer_orders = Order.objects.filter(
            customer=customer,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        if customer_orders > top_customer_orders:
            top_customer = customer.user
            top_customer_orders = customer_orders
    
    # Get or create user report result
    user_result, created = UserReportResult.objects.get_or_create(
        report=report,
        defaults={
            'total_active_users': active_users.count(),
            'new_customers': new_customers,
            'active_account_managers': active_managers,
            'top_performing_account_manager': top_manager,
            'top_customer': top_customer,
            'total_orders_by_top_manager': top_manager_orders,
            'total_revenue_by_top_manager': top_manager_revenue
        }
    )
    
    if not created:
        # Update existing report
        user_result.total_active_users = active_users.count()
        user_result.new_customers = new_customers
        user_result.active_account_managers = active_managers
        user_result.top_performing_account_manager = top_manager
        user_result.top_customer = top_customer
        user_result.total_orders_by_top_manager = top_manager_orders
        user_result.total_revenue_by_top_manager = top_manager_revenue
        user_result.save()
    
    return user_result