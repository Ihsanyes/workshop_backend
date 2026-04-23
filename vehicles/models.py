"""
App: vehicles
Depends on: users
"""

from django.db import models
from django.utils import timezone


class VehicleType(models.TextChoices):
    TWO_WHEELER   = '2W', 'Two Wheeler'
    THREE_WHEELER = '3W', 'Three Wheeler'
    FOUR_WHEELER  = '4W', 'Four Wheeler'
    HEAVY         = 'HV', 'Heavy Vehicle'


class FuelType(models.TextChoices):
    PETROL   = 'PETROL',   'Petrol'
    DIESEL   = 'DIESEL',   'Diesel'
    ELECTRIC = 'ELECTRIC', 'Electric'
    CNG      = 'CNG',      'CNG'


class VehicleBrand(models.Model):
    workshop = models.ForeignKey(
        'users.Workshop', on_delete=models.CASCADE,
        null=True, blank=True, db_index=True
    )
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ['name', 'workshop']

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    workshop     = models.ForeignKey(
        'users.Workshop', on_delete=models.CASCADE,
        null=True, blank=True, db_index=True
    )
    brand        = models.ForeignKey(VehicleBrand, on_delete=models.CASCADE, related_name='models')
    model_name   = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=2, choices=VehicleType.choices, default=VehicleType.TWO_WHEELER)

    class Meta:
        unique_together = ['brand', 'model_name', 'workshop']

    def __str__(self):
        return f"{self.brand.name} {self.model_name}"


class Customer(models.Model):
    workshop   = models.ForeignKey(
        'users.Workshop', on_delete=models.CASCADE,
        db_index=True, related_name='customers'
    )
    name       = models.CharField(max_length=150)
    phone      = models.CharField(max_length=15)
    email      = models.EmailField(blank=True)
    address    = models.TextField(blank=True)
    gstin      = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['phone', 'workshop']
        ordering        = ['name']
        indexes         = [models.Index(fields=['workshop', 'phone'])]

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Vehicle(models.Model):
    workshop        = models.ForeignKey(
        'users.Workshop', on_delete=models.CASCADE,
        db_index=True, related_name='vehicles'
    )
    customer        = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_model   = models.ForeignKey(VehicleModel, on_delete=models.PROTECT, related_name='registered_vehicles')
    registration_no = models.CharField(max_length=20)
    chassis_no      = models.CharField(max_length=50, blank=True)
    engine_no       = models.CharField(max_length=50, blank=True)
    color           = models.CharField(max_length=50, blank=True)
    year            = models.PositiveSmallIntegerField(null=True, blank=True)
    fuel_type       = models.CharField(max_length=10, choices=FuelType.choices, blank=True)
    odometer_km     = models.PositiveIntegerField(default=0)
    # Compliance dates
    insurance_expiry = models.DateField(null=True, blank=True)
    puc_expiry       = models.DateField(null=True, blank=True)
    permit_expiry    = models.DateField(null=True, blank=True)   # Heavy vehicle
    fitness_expiry   = models.DateField(null=True, blank=True)  # Heavy vehicle
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    @property
    def vehicle_type(self):
        return self.vehicle_model.vehicle_type

    class Meta:
        unique_together = ['registration_no', 'workshop']
        indexes         = [
            models.Index(fields=['workshop', 'registration_no']),
        ]

    def __str__(self):
        return f"{self.registration_no} – {self.vehicle_model}"
