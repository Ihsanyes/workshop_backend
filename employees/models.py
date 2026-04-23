"""
App: employees
Depends on: users

Note: Employee = users.User (role='staff').
      This app adds HR-specific data on top.
"""

from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT  = 'PRESENT',  'Present'
        ABSENT   = 'ABSENT',   'Absent'
        HALF_DAY = 'HALF_DAY', 'Half Day'
        HOLIDAY  = 'HOLIDAY',  'Holiday'
        LEAVE    = 'LEAVE',    'On Leave'

    workshop   = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True, related_name='attendances')
    employee   = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='attendances')
    date       = models.DateField()
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    check_in   = models.TimeField(null=True, blank=True)
    check_out  = models.TimeField(null=True, blank=True)
    notes      = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'date']
        ordering        = ['-date']
        indexes         = [models.Index(fields=['workshop', 'date'])]

    def __str__(self):
        return f"{self.employee.get_full_name()} | {self.date} | {self.status}"


class LeaveRequest(models.Model):
    class LeaveType(models.TextChoices):
        CASUAL   = 'CASUAL',   'Casual Leave'
        SICK     = 'SICK',     'Sick Leave'
        EARNED   = 'EARNED',   'Earned Leave'
        UNPAID   = 'UNPAID',   'Unpaid Leave'

    class Status(models.TextChoices):
        PENDING  = 'PENDING',  'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    workshop    = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True, related_name='leave_requests')
    employee    = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type  = models.CharField(max_length=10, choices=LeaveType.choices)
    from_date   = models.DateField()
    to_date     = models.DateField()
    reason      = models.TextField()
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leave_approvals'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} | {self.leave_type} | {self.from_date} to {self.to_date}"


class SalaryRecord(models.Model):
    """Monthly salary record per employee."""
    workshop       = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True, related_name='salary_records')
    employee       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='salary_records')
    month          = models.PositiveSmallIntegerField()   # 1–12
    year           = models.PositiveSmallIntegerField()
    base_salary    = models.DecimalField(max_digits=10, decimal_places=2)
    allowances     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid        = models.BooleanField(default=False)
    paid_on        = models.DateField(null=True, blank=True)
    payment_mode   = models.CharField(max_length=20, blank=True,
                       choices=[('CASH','Cash'), ('BANK','Bank Transfer'), ('UPI','UPI')])
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering        = ['-year', '-month']

    def __str__(self):
        return f"{self.employee.get_full_name()} | {self.month}/{self.year} | ₹{self.net_salary}"


class PerformanceNote(models.Model):
    """Simple manager notes on employee performance."""
    workshop   = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True)
    employee   = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='performance_notes')
    noted_by   = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='performance_given')
    note       = models.TextField()
    rating     = models.PositiveSmallIntegerField(
                   null=True, blank=True,
                   help_text='1 (poor) to 5 (excellent)'
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} | rating={self.rating}"
