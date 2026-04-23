from rest_framework import serializers
from inventory.models import (
    Brand, Category, Product, ProductVariant,
    Stock, StockAlert, Supplier,
    PurchaseOrder, PurchaseOrderItem, PriceHistory
)


# ──────────────────────────────────────────
# BRAND
# ──────────────────────────────────────────

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Brand
        fields = ['id', 'name', 'description', 'created_at']

    def validate_name(self, value):
        workshop = self.context.get('workshop')
        qs = Brand.objects.filter(name__iexact=value, workshop=workshop)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Brand with this name already exists")
        return value

    def create(self, validated_data):
        validated_data['workshop'] = self.context['workshop']
        return super().create(validated_data)


# ──────────────────────────────────────────
# CATEGORY
# ──────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'description', 'created_at']

    def validate_name(self, value):
        workshop = self.context.get('workshop')
        qs = Category.objects.filter(name__iexact=value, workshop=workshop)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Category with this name already exists")
        return value

    def create(self, validated_data):
        validated_data['workshop'] = self.context['workshop']
        return super().create(validated_data)


# ──────────────────────────────────────────
# PRODUCT
# ──────────────────────────────────────────

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model  = Product
        fields = ['id', 'name', 'category', 'category_name', 'description', 'unit', 'is_active', 'created_at']

    def validate(self, data):
        workshop = self.context.get('workshop')
        category = data.get('category', getattr(self.instance, 'category', None))
        name     = data.get('name', getattr(self.instance, 'name', None))

        qs = Product.objects.filter(name__iexact=name, category=category, workshop=workshop)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Product with this name already exists in this category")
        return data

    def create(self, validated_data):
        validated_data['workshop'] = self.context['workshop']
        return super().create(validated_data)


# ──────────────────────────────────────────
# PRODUCT VARIANT
# ──────────────────────────────────────────

class ProductVariantSerializer(serializers.ModelSerializer):
    product_name      = serializers.CharField(source='product.name', read_only=True)
    brand_name        = serializers.CharField(source='brand.name', read_only=True)
    current_stock     = serializers.SerializerMethodField()

    class Meta:
        model  = ProductVariant
        fields = [
            'id', 'product', 'product_name', 'brand', 'brand_name',
            'variant_name', 'sku', 'barcode',
            'cost_price', 'selling_price',
            'compatible_vehicles', 'is_active',
            'current_stock', 'created_at'
        ]

    def get_current_stock(self, obj):
        workshop = self.context.get('workshop')
        stock = obj.stock.filter(workshop=workshop).first()
        return stock.quantity if stock else 0

    def validate_sku(self, value):
        workshop = self.context.get('workshop')
        qs = ProductVariant.objects.filter(sku=value, workshop=workshop)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("SKU already exists")
        return value

    def validate(self, data):
        # Ensure brand & product belong to same workshop
        workshop = self.context.get('workshop')
        brand   = data.get('brand')
        product = data.get('product')
        if brand and brand.workshop != workshop:
            raise serializers.ValidationError("Brand does not belong to your workshop")
        if product and product.workshop != workshop:
            raise serializers.ValidationError("Product does not belong to your workshop")
        return data

    def create(self, validated_data):
        workshop = self.context['workshop']
        validated_data['workshop'] = workshop
        variant = super().create(validated_data)
        # Auto-create Stock record
        Stock.objects.get_or_create(workshop=workshop, product_variant=variant)
        return variant


# ──────────────────────────────────────────
# STOCK
# ──────────────────────────────────────────

class StockSerializer(serializers.ModelSerializer):
    product_name  = serializers.CharField(source='product_variant.product.name', read_only=True)
    variant_name  = serializers.CharField(source='product_variant.variant_name', read_only=True)
    sku           = serializers.CharField(source='product_variant.sku', read_only=True)
    brand_name    = serializers.CharField(source='product_variant.brand.name', read_only=True)
    selling_price = serializers.DecimalField(source='product_variant.selling_price', max_digits=10, decimal_places=2, read_only=True)
    is_low        = serializers.SerializerMethodField()

    class Meta:
        model  = Stock
        fields = [
            'id', 'product_variant', 'product_name', 'variant_name',
            'sku', 'brand_name', 'selling_price', 'quantity', 'is_low', 'updated_at'
        ]

    def get_is_low(self, obj):
        alert = obj.product_variant.alert_setting.filter(workshop=obj.workshop).first()
        if alert:
            return alert.is_low(obj.quantity)
        return False


class StockAdjustSerializer(serializers.Serializer):
    """Manual stock adjustment — owner/manager only."""
    product_variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all())
    quantity        = serializers.IntegerField(help_text='Positive = add, Negative = remove')
    reason          = serializers.CharField(max_length=255)

    def validate_product_variant(self, value):
        workshop = self.context.get('workshop')
        if value.workshop != workshop:
            raise serializers.ValidationError("Product variant not found in your workshop")
        return value


# ──────────────────────────────────────────
# STOCK ALERT
# ──────────────────────────────────────────

class StockAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)
    sku          = serializers.CharField(source='product_variant.sku', read_only=True)

    class Meta:
        model  = StockAlert
        fields = ['id', 'product_variant', 'product_name', 'sku', 'min_stock', 'max_stock', 'is_active']

    def validate_product_variant(self, value):
        workshop = self.context.get('workshop')
        if value.workshop != workshop:
            raise serializers.ValidationError("Product variant not found in your workshop")
        return value

    def create(self, validated_data):
        validated_data['workshop'] = self.context['workshop']
        # upsert — if alert already exists, update it
        instance, _ = StockAlert.objects.update_or_create(
            workshop=validated_data['workshop'],
            product_variant=validated_data['product_variant'],
            defaults=validated_data
        )
        return instance


# ──────────────────────────────────────────
# SUPPLIER
# ──────────────────────────────────────────

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Supplier
        fields = ['id', 'name', 'contact_name', 'phone', 'email', 'address', 'gstin', 'credit_days', 'is_active', 'created_at']

    def validate_name(self, value):
        workshop = self.context.get('workshop')
        qs = Supplier.objects.filter(name__iexact=value, workshop=workshop)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Supplier with this name already exists")
        return value

    def create(self, validated_data):
        validated_data['workshop'] = self.context['workshop']
        return super().create(validated_data)


# ──────────────────────────────────────────
# PURCHASE ORDER
# ──────────────────────────────────────────

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)
    sku          = serializers.CharField(source='product_variant.sku', read_only=True)
    pending_qty  = serializers.IntegerField(read_only=True)

    class Meta:
        model  = PurchaseOrderItem
        fields = [
            'id', 'product_variant', 'product_name', 'sku',
            'ordered_qty', 'received_qty', 'pending_qty',
            'unit_cost', 'tax_rate', 'line_total'
        ]
        read_only_fields = ['received_qty', 'line_total']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items        = PurchaseOrderItemSerializer(many=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model  = PurchaseOrder
        fields = [
            'id', 'po_number', 'supplier', 'supplier_name', 'status',
            'order_date', 'expected_date', 'received_date',
            'subtotal', 'tax_amount', 'total_amount',
            'notes', 'items', 'created_at'
        ]
        read_only_fields = ['po_number', 'status', 'subtotal', 'tax_amount', 'total_amount']

    def validate_supplier(self, value):
        workshop = self.context.get('workshop')
        if value.workshop != workshop:
            raise serializers.ValidationError("Supplier not found in your workshop")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        return value

    def create(self, validated_data):
        from inventory.services import generate_po_number, calculate_po_totals
        items_data = validated_data.pop('items')
        workshop   = self.context['workshop']
        user       = self.context['request'].user

        validated_data['workshop']   = workshop
        validated_data['created_by'] = user
        validated_data['po_number']  = generate_po_number(workshop)

        po = PurchaseOrder.objects.create(**validated_data)

        subtotal = tax_total = 0
        for item_data in items_data:
            qty       = item_data['ordered_qty']
            unit_cost = item_data['unit_cost']
            tax_rate  = item_data.get('tax_rate', 18)
            tax_amt   = round(unit_cost * qty * tax_rate / 100, 2)
            line_total = round(unit_cost * qty + tax_amt, 2)

            PurchaseOrderItem.objects.create(
                purchase_order=po,
                line_total=line_total,
                **item_data
            )
            subtotal  += unit_cost * qty
            tax_total += tax_amt

        po.subtotal     = round(subtotal, 2)
        po.tax_amount   = round(tax_total, 2)
        po.total_amount = round(subtotal + tax_total, 2)
        po.save()

        return po


class GRNSerializer(serializers.Serializer):
    """Goods Receipt Note — mark items as received, triggers StockMovement."""
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text='[{"item_id": 1, "received_qty": 10}, ...]'
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Items are required")
        for item in value:
            if 'item_id' not in item or 'received_qty' not in item:
                raise serializers.ValidationError("Each item needs item_id and received_qty")
            if int(item['received_qty']) <= 0:
                raise serializers.ValidationError("received_qty must be greater than 0")
        return value


# ──────────────────────────────────────────
# PRICE HISTORY
# ──────────────────────────────────────────

class PriceHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)
    sku          = serializers.CharField(source='product_variant.sku', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model  = PriceHistory
        fields = [
            'id', 'product_variant', 'product_name', 'sku',
            'old_cost_price', 'new_cost_price',
            'old_selling_price', 'new_selling_price',
            'changed_by_name', 'reason', 'changed_at'
        ]
