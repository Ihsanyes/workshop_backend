"""
App: finance
Depends on: users, jobs, vehicles
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Invoice(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID  = 'UNPAID',  'Unpaid'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        PAID    = 'PAID',    'Paid'

    class PaymentMode(models.TextChoices):
        CASH   = 'CASH',   'Cash'
        UPI    = 'UPI',    'UPI'
        CARD   = 'CARD',   'Card'
        NEFT   = 'NEFT',   'NEFT / Bank Transfer'
        CREDIT = 'CREDIT', 'Credit'

    workshop        = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True, related_name='invoices')
    job_card        = models.OneToOneField('jobs.JobCard', on_delete=models.PROTECT, related_name='invoice')
    customer        = models.ForeignKey('vehicles.Customer', on_delete=models.PROTECT, related_name='invoices')
    invoice_number  = models.CharField(max_length=30, unique=True)
    invoice_date    = models.DateField(default=timezone.now)
    parts_total     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labour_total    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status  = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    payment_mode    = models.CharField(max_length=10, choices=PaymentMode.choices, blank=True)
    notes           = models.TextField(blank=True)
    created_by      = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='invoices_created')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date']
        indexes  = [models.Index(fields=['workshop', 'payment_status'])]

    def __str__(self):
        return f"INV#{self.invoice_number} | {self.customer.name}"


class Payment(models.Model):
    """One invoice can have multiple partial payments."""
    invoice         = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount          = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_date    = models.DateField(default=timezone.now)
    payment_mode    = models.CharField(max_length=10, choices=Invoice.PaymentMode.choices)
    transaction_ref = models.CharField(max_length=100, blank=True)
    received_by     = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='payments_received')
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"₹{self.amount} → INV#{self.invoice.invoice_number}"


class Expense(models.Model):
    """Workshop expenses — rent, utilities, tools, etc."""
    class Category(models.TextChoices):
        RENT        = 'RENT',        'Rent'
        UTILITIES   = 'UTILITIES',   'Utilities'
        SALARY      = 'SALARY',      'Salary'
        TOOLS       = 'TOOLS',       'Tools & Equipment'
        MARKETING   = 'MARKETING',   'Marketing'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'
        OTHER       = 'OTHER',       'Other'

    workshop      = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True, related_name='expenses')
    category      = models.CharField(max_length=20, choices=Category.choices)
    title         = models.CharField(max_length=200)
    amount        = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    expense_date  = models.DateField(default=timezone.now)
    paid_to       = models.CharField(max_length=150, blank=True)
    payment_mode  = models.CharField(max_length=10, choices=Invoice.PaymentMode.choices, blank=True)
    receipt_ref   = models.CharField(max_length=100, blank=True)
    notes         = models.TextField(blank=True)
    created_by    = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='expenses_created')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']
        indexes  = [models.Index(fields=['workshop', 'expense_date'])]

    def __str__(self):
        return f"{self.category} | ₹{self.amount} | {self.expense_date}"
