"""
inventory/services.py
Helper functions used by serializers and signals.
"""

from django.db import transaction


def generate_po_number(workshop):
    """
    Thread-safe PO number generator per workshop.
    Format: W{workshop_id}PO{0001}
    """
    from inventory.models import PurchaseOrder
    with transaction.atomic():
        last = (
            PurchaseOrder.objects
            .filter(workshop=workshop)
            .order_by('-id')
            .first()
        )
        number = (last.id + 1) if last else 1
    return f"W{workshop.id}PO{str(number).zfill(4)}"


def apply_grn(purchase_order, items_data, received_by):
    """
    Process GRN for a PurchaseOrder.
    - Updates PurchaseOrderItem.received_qty
    - Creates StockMovement (PURCHASE)
    - Updates Stock.quantity
    - Updates PurchaseOrder.status
    """
    from inventory.models import PurchaseOrderItem, Stock, StockMovement

    with transaction.atomic():
        all_received = True

        for item_data in items_data:
            item_id      = item_data['item_id']
            received_qty = int(item_data['received_qty'])

            try:
                item = PurchaseOrderItem.objects.select_for_update().get(
                    id=item_id,
                    purchase_order=purchase_order
                )
            except PurchaseOrderItem.DoesNotExist:
                continue

            # Cap received_qty to pending
            receivable = item.ordered_qty - item.received_qty
            qty_to_add = min(received_qty, receivable)

            if qty_to_add <= 0:
                continue

            item.received_qty += qty_to_add
            item.save()

            # Stock Movement
            StockMovement.objects.create(
                workshop        = purchase_order.workshop,
                product_variant = item.product_variant,
                movement_type   = 'PURCHASE',
                quantity        = qty_to_add,
                unit_cost       = item.unit_cost,
                purchase_order  = purchase_order,
                reference_note  = f"GRN for {purchase_order.po_number}",
                moved_by        = received_by,
            )

            # Update Stock
            stock, _ = Stock.objects.select_for_update().get_or_create(
                workshop        = purchase_order.workshop,
                product_variant = item.product_variant,
            )
            stock.quantity += qty_to_add
            stock.save()

            if item.received_qty < item.ordered_qty:
                all_received = False

        # Update PO status
        any_received = purchase_order.items.filter(received_qty__gt=0).exists()
        if all_received and any_received:
            purchase_order.status = 'RECEIVED'
        elif any_received:
            purchase_order.status = 'PARTIAL'
        purchase_order.save()

    return purchase_order


def apply_stock_adjustment(workshop, product_variant, quantity, reason, moved_by):
    """
    Manual stock adjustment.
    quantity > 0 = add stock, quantity < 0 = remove stock
    """
    from inventory.models import Stock, StockMovement

    with transaction.atomic():
        stock, _ = Stock.objects.select_for_update().get_or_create(
            workshop=workshop,
            product_variant=product_variant
        )

        # Prevent negative stock
        if stock.quantity + quantity < 0:
            raise ValueError("Insufficient stock for this adjustment")

        stock.quantity += quantity
        stock.save()

        StockMovement.objects.create(
            workshop        = workshop,
            product_variant = product_variant,
            movement_type   = 'ADJUSTMENT',
            quantity        = quantity,
            reference_note  = reason,
            moved_by        = moved_by,
        )

    return stock
