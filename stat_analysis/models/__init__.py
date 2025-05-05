"""
Model initialization for stat_analysis app.
"""
from .report import Report
from .statistics import JobReportResult, OrderReportResult, UserReportResult

__all__ = ['Report', 'JobReportResult', 'OrderReportResult', 'UserReportResult']