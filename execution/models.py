"""execution.models.py

This script defines the Job model which is used to track
the execution progress of customer orders.
"""
from django.db import models
from provider_services.models import Order, ServiceProvider


class Job(models.Model):
    """
    Model representing jobs that execute customer orders.
    A job can contain multiple orders from the same service provider.
    """
    JOB_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('wafer_run', 'Wafer Run'),
    ]
    STATE_CHOICES = [
        ('created', 'Created'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('delayed', 'Delayed'),
    ]

    job_id = models.CharField(max_length=10, unique=True)
    job_name = models.CharField(max_length=200)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='jobs')
    
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)

    starting_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    completion_time = models.FloatField(
        help_text="Time in days which were spent to complete the job.",
        null=True, blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_name} ({self.job_id})"
    
    def calculate_completion_time(self):
        """Calculate the completion time if end_date is available."""
        if self.end_date and self.starting_date:
            delta = self.end_date - self.starting_date
            self.completion_time = delta.total_seconds() / (24 * 3600)  # Convert to days
            self.save(update_fields=['completion_time'])
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # If the job is marked as completed and completion_time is not set,
        # calculate it automatically
        if self.state == 'completed' and not self.completion_time and self.end_date:
            self.calculate_completion_time()