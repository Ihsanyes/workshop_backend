"""
App: jobs
Depends on: users, inventory, vehicles
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class JobCard(models.Model):
    class Status(models.TextChoices):
        PENDING     = 'PENDING',     'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        ON_HOLD     = 'ON_HOLD',     'On Hold'
        COMPLETED   = 'COMPLETED',   'Completed'
        DELIVERED   = 'DELIVERED',   'Delivered'
        CANCELLED   = 'CANCELLED',   'Cancelled'

    workshop     = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True, related_name='job_cards')
    job_number   = models.CharField(max_length=30, unique=True)
    vehicle      = models.ForeignKey('vehicles.Vehicle', on_delete=models.PROTECT, related_name='job_cards')
    customer     = models.ForeignKey('vehicles.Customer', on_delete=models.PROTECT, related_name='job_cards')
    status       = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING, db_index=True)
    odometer_in  = models.PositiveIntegerField()
    odometer_out = models.PositiveIntegerField(null=True, blank=True)
    complaint    = models.TextField(verbose_name='Customer Complaint')
    diagnosis    = models.TextField(blank=True)
    work_done    = models.TextField(blank=True)
    technician   = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_job_cards'
    )
    received_at  = models.DateTimeField(default=timezone.now)
    promised_at  = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_by   = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_job_cards')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['workshop', 'status']),
            models.Index(fields=['workshop', 'created_at']),
        ]

    def __str__(self):
        return f"JC#{self.job_number} | {self.vehicle.registration_no}"


class JobCardService(models.Model):
    """Labour / service line — oil change, wheel alignment, etc."""
    job_card      = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='services')
    service_name  = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    labour_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    is_completed  = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.service_name} → JC#{self.job_card.job_number}"


class JobCardPart(models.Model):
    """
    Parts issued to a job.
    On save → signal creates StockMovement(JOB_ISSUE) → Stock.quantity decreases.
    On is_returned=True → signal creates StockMovement(JOB_RETURN) → Stock.quantity restored.
    """
    job_card        = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='parts_used')
    product_variant = models.ForeignKey('inventory.ProductVariant', on_delete=models.PROTECT, related_name='job_card_uses')
    quantity        = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price      = models.DecimalField(max_digits=10, decimal_places=2)
    discount_pct    = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_returned     = models.BooleanField(default=False)
    issued_by       = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='parts_issued')
    issued_at       = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product_variant} × {self.quantity} → JC#{self.job_card.job_number}"


class StockMovement(models.Model):
    """
    Full audit trail of every stock change.
    quantity > 0 = IN (purchase / return)
    quantity < 0 = OUT (job issue / scrap)
    Never update Stock.quantity directly — always go through this model.
    """
    class MovementType(models.TextChoices):
        PURCHASE   = 'PURCHASE',   'Purchase / GRN'
        JOB_ISSUE  = 'JOB_ISSUE',  'Issued to Job'
        JOB_RETURN = 'JOB_RETURN', 'Returned from Job'
        SUP_RETURN = 'SUP_RETURN', 'Returned to Supplier'
        ADJUSTMENT = 'ADJUSTMENT', 'Manual Adjustment'
        SCRAP      = 'SCRAP',      'Scrap / Write-off'

    workshop        = models.ForeignKey('users.Workshop', on_delete=models.CASCADE, db_index=True, related_name='stock_movements')
    product_variant = models.ForeignKey('inventory.ProductVariant', on_delete=models.PROTECT, related_name='movements')
    movement_type   = models.CharField(max_length=20, choices=MovementType.choices)
    quantity        = models.IntegerField()
    unit_cost       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_order  = models.ForeignKey('inventory.PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    job_card        = models.ForeignKey(JobCard, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    reference_note  = models.CharField(max_length=255, blank=True)
    moved_by        = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='stock_movements')
    moved_at        = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-moved_at']
        indexes  = [
            models.Index(fields=['workshop', 'product_variant']),
            models.Index(fields=['workshop', 'movement_type']),
        ]

    def __str__(self):
        d = '▲ IN' if self.quantity > 0 else '▼ OUT'
        return f"{d} {abs(self.quantity)} × {self.product_variant} [{self.movement_type}]"
