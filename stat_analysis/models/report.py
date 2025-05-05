"""stat_analysis.models.report.py

This script defines the Report model for generating statistical reports.
"""
from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):
    """
    Model representing statistical reports that can be generated for various time periods.
    """
    # Report types
    REPORT_TYPE_CHOICES = [
        ('job', 'Job Analysis'),
        ('order', 'Order Analysis'),
        ('user', 'User Activity Analysis'),
        ('combined', 'Combined Analysis'),
    ]
    
    # Quarter choices
    QUARTER_CHOICES = [
        ('Q1', 'Q1 (Jan-Mar)'),
        ('Q2', 'Q2 (Apr-Jun)'),
        ('Q3', 'Q3 (Jul-Sep)'),
        ('Q4', 'Q4 (Oct-Dec)'),
    ]
    
    # Metadata
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='combined')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    
    # Report settings 
    quarter_from = models.CharField(max_length=2, choices=QUARTER_CHOICES)
    year_from = models.IntegerField()
    quarter_to = models.CharField(max_length=2, choices=QUARTER_CHOICES)
    year_to = models.IntegerField()
    
    # PDF attachment
    pdf_report = models.FileField(upload_to='reports/pdf/', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()}, {self.year_from} {self.quarter_from} - {self.year_to} {self.quarter_to})"
    
    def save(self, *args, **kwargs):
        """
        Override save method to trigger statistics calculation when report is created or updated
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Import here to avoid circular imports
        from stat_analysis.stat_utils import calculate_report_statistics
        
        # Calculate statistics for this report
        calculate_report_statistics(self)