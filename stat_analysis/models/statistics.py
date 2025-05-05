"""stat_analysis.models.statistics.py

This script defines models for storing statistical results from various reports.
"""
from django.db import models
from django.contrib.auth.models import User

from .report import Report


class JobReportResult(models.Model):
    """
    Model to store analysis results for the Jobs.
    
    Includes expanded statistics such as average completion time per job type
    and job counts per status.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='job_result')

    # Total job statistics
    total_jobs = models.IntegerField(default=0)
    
    # Average completion time per job type
    avg_completion_time_regular = models.FloatField(null=True, blank=True, 
                                                   help_text="Average completion time in days for regular jobs")
    avg_completion_time_wafer_run = models.FloatField(null=True, blank=True, 
                                                     help_text="Average completion time in days for wafer run jobs")
    
    # Job counts by status
    jobs_created = models.IntegerField(default=0)
    jobs_active = models.IntegerField(default=0)
    jobs_completed = models.IntegerField(default=0)
    jobs_failed = models.IntegerField(default=0)
    jobs_delayed = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Job Report Result"
        verbose_name_plural = "Job Report Results"
    
    def __str__(self):
        return f"Job Statistics for {self.report.title}"


class OrderReportResult(models.Model):
    """
    Model to store analysis results for the customer Orders.
    
    Expanded with more detailed metrics on order performance.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='order_result')

    # Basic order statistics
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Order status statistics
    orders_draft = models.IntegerField(default=0)
    orders_submitted = models.IntegerField(default=0)
    orders_in_progress = models.IntegerField(default=0)
    orders_completed = models.IntegerField(default=0)
    orders_cancelled = models.IntegerField(default=0)
    
    # Time-related statistics
    avg_processing_time = models.FloatField(null=True, blank=True, 
                                           help_text="Average time in days from order submission to completion")
    
    class Meta:
        verbose_name = "Order Report Result"
        verbose_name_plural = "Order Report Results"
    
    def __str__(self):
        return f"Order Statistics for {self.report.title}"


class UserReportResult(models.Model):
    """
    Model to store analysis results for User activity.
    
    Tracks metrics related to user activity and engagement.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='user_result')
    
    # User activity metrics
    total_active_users = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    active_account_managers = models.IntegerField(default=0)
    
    # Top performers
    top_performing_account_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name='top_performer_reports'
    )
    top_customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='top_customer_reports'
    )
    
    # Performance metrics
    total_orders_by_top_manager = models.IntegerField(default=0)
    total_revenue_by_top_manager = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "User Report Result"
        verbose_name_plural = "User Report Results"
    
    def __str__(self):
        return f"User Activity Statistics for {self.report.title}"