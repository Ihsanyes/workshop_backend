"""
inventory/signals.py
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from inventory.models import ProductVariant, PriceHistory


@receiver(pre_save, sender=ProductVariant)
def track_price_change(sender, instance, **kwargs):
    """
    Auto-create PriceHistory when cost_price or selling_price changes.
    """
    if not instance.pk:
        return  # New object — no history needed

    try:
        old = ProductVariant.objects.get(pk=instance.pk)
    except ProductVariant.DoesNotExist:
        return

    price_changed = (
        old.cost_price    != instance.cost_price or
        old.selling_price != instance.selling_price
    )

    if price_changed:
        PriceHistory.objects.create(
            workshop          = instance.workshop,
            product_variant   = instance,
            old_cost_price    = old.cost_price,
            new_cost_price    = instance.cost_price,
            old_selling_price = old.selling_price,
            new_selling_price = instance.selling_price,
        )
