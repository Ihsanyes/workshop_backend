"""
inventory/views.py
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.permission import IsOwnerOrSuperUser, HasModulePermission
from inventory.models import (
    Brand, Category, Product, ProductVariant,
    Stock, StockAlert, Supplier, PurchaseOrder, PriceHistory
)
from inventory.serializers import (
    BrandSerializer, CategorySerializer,
    ProductSerializer, ProductVariantSerializer,
    StockSerializer, StockAdjustSerializer, StockAlertSerializer,
    SupplierSerializer,
    PurchaseOrderSerializer, GRNSerializer,
    PriceHistorySerializer
)
from inventory.services import apply_grn, apply_stock_adjustment


def get_workshop(request):
    return request.user.workshop


# ──────────────────────────────────────────
# BRAND
# ──────────────────────────────────────────

class BrandListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        brands = Brand.objects.filter(workshop=get_workshop(request))
        return Response(BrandSerializer(brands, many=True).data)

    def post(self, request):
        s = BrandSerializer(data=request.data, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "brand": s.data}, status=201)
        return Response({"status": "0", "errors": s.errors}, status=400)


class BrandDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, workshop):
        try:
            return Brand.objects.get(pk=pk, workshop=workshop)
        except Brand.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Brand not found"}, status=404)
        return Response(BrandSerializer(obj).data)

    def patch(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Brand not found"}, status=404)
        s = BrandSerializer(obj, data=request.data, partial=True, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "brand": s.data})
        return Response({"status": "0", "errors": s.errors}, status=400)

    def delete(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Brand not found"}, status=404)
        obj.delete()
        return Response({"status": "1", "message": "Brand deleted"})


# ──────────────────────────────────────────
# CATEGORY
# ──────────────────────────────────────────

class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cats = Category.objects.filter(workshop=get_workshop(request))
        return Response(CategorySerializer(cats, many=True).data)

    def post(self, request):
        s = CategorySerializer(data=request.data, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "category": s.data}, status=201)
        return Response({"status": "0", "errors": s.errors}, status=400)


class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, workshop):
        try:
            return Category.objects.get(pk=pk, workshop=workshop)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Category not found"}, status=404)
        return Response(CategorySerializer(obj).data)

    def patch(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Category not found"}, status=404)
        s = CategorySerializer(obj, data=request.data, partial=True, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "category": s.data})
        return Response({"status": "0", "errors": s.errors}, status=400)

    def delete(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Category not found"}, status=404)
        obj.delete()
        return Response({"status": "1", "message": "Category deleted"})


# ──────────────────────────────────────────
# PRODUCT
# ──────────────────────────────────────────

class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(
            workshop=get_workshop(request)
        ).select_related('category')
        return Response(ProductSerializer(products, many=True, context={'workshop': get_workshop(request)}).data)

    def post(self, request):
        s = ProductSerializer(data=request.data, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "product": s.data}, status=201)
        return Response({"status": "0", "errors": s.errors}, status=400)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, workshop):
        try:
            return Product.objects.get(pk=pk, workshop=workshop)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Product not found"}, status=404)
        return Response(ProductSerializer(obj, context={'workshop': get_workshop(request)}).data)

    def patch(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Product not found"}, status=404)
        s = ProductSerializer(obj, data=request.data, partial=True, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "product": s.data})
        return Response({"status": "0", "errors": s.errors}, status=400)

    def delete(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Product not found"}, status=404)
        obj.delete()
        return Response({"status": "1", "message": "Product deleted"})


# ──────────────────────────────────────────
# PRODUCT VARIANT
# ──────────────────────────────────────────

class ProductVariantListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workshop = get_workshop(request)
        variants = ProductVariant.objects.filter(
            workshop=workshop
        ).select_related('product', 'brand').prefetch_related('stock')

        # Optional filter by product
        product_id = request.query_params.get('product')
        if product_id:
            variants = variants.filter(product_id=product_id)

        return Response(
            ProductVariantSerializer(variants, many=True, context={'workshop': workshop}).data
        )

    def post(self, request):
        workshop = get_workshop(request)
        s = ProductVariantSerializer(data=request.data, context={'workshop': workshop, 'request': request})
        if s.is_valid():
            variant = s.save()
            return Response({"status": "1", "variant": ProductVariantSerializer(variant, context={'workshop': workshop}).data}, status=201)
        return Response({"status": "0", "errors": s.errors}, status=400)


class ProductVariantDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, workshop):
        try:
            return ProductVariant.objects.get(pk=pk, workshop=workshop)
        except ProductVariant.DoesNotExist:
            return None

    def get(self, request, pk):
        workshop = get_workshop(request)
        obj = self._get_object(pk, workshop)
        if not obj:
            return Response({"status": "0", "message": "Variant not found"}, status=404)
        return Response(ProductVariantSerializer(obj, context={'workshop': workshop}).data)

    def patch(self, request, pk):
        workshop = get_workshop(request)
        obj = self._get_object(pk, workshop)
        if not obj:
            return Response({"status": "0", "message": "Variant not found"}, status=404)
        s = ProductVariantSerializer(obj, data=request.data, partial=True, context={'workshop': workshop})
        if s.is_valid():
            variant = s.save()
            return Response({"status": "1", "variant": ProductVariantSerializer(variant, context={'workshop': workshop}).data})
        return Response({"status": "0", "errors": s.errors}, status=400)

    def delete(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Variant not found"}, status=404)
        obj.delete()
        return Response({"status": "1", "message": "Variant deleted"})


# ──────────────────────────────────────────
# STOCK
# ──────────────────────────────────────────

class StockListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workshop = get_workshop(request)
        stocks   = Stock.objects.filter(
            workshop=workshop
        ).select_related('product_variant__product', 'product_variant__brand')

        # Filter: low stock only
        if request.query_params.get('low_stock') == 'true':
            low_ids = []
            for s in stocks:
                alert = s.product_variant.alert_setting.filter(workshop=workshop).first()
                if alert and alert.is_low(s.quantity):
                    low_ids.append(s.id)
            stocks = stocks.filter(id__in=low_ids)

        return Response(
            StockSerializer(stocks, many=True, context={'workshop': workshop}).data
        )


class StockAdjustView(APIView):
    permission_classes = [IsOwnerOrSuperUser]

    def post(self, request):
        workshop = get_workshop(request)
        s = StockAdjustSerializer(data=request.data, context={'workshop': workshop})
        if s.is_valid():
            try:
                stock = apply_stock_adjustment(
                    workshop        = workshop,
                    product_variant = s.validated_data['product_variant'],
                    quantity        = s.validated_data['quantity'],
                    reason          = s.validated_data['reason'],
                    moved_by        = request.user,
                )
                return Response({
                    "status": "1",
                    "message": "Stock adjusted",
                    "new_quantity": stock.quantity
                })
            except ValueError as e:
                return Response({"status": "0", "message": str(e)}, status=400)
        return Response({"status": "0", "errors": s.errors}, status=400)


# ──────────────────────────────────────────
# STOCK ALERT
# ──────────────────────────────────────────

class StockAlertListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = StockAlert.objects.filter(workshop=get_workshop(request))
        return Response(StockAlertSerializer(alerts, many=True).data)

    def post(self, request):
        s = StockAlertSerializer(data=request.data, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "alert": s.data}, status=201)
        return Response({"status": "0", "errors": s.errors}, status=400)


# ──────────────────────────────────────────
# SUPPLIER
# ──────────────────────────────────────────

class SupplierListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suppliers = Supplier.objects.filter(workshop=get_workshop(request))
        return Response(SupplierSerializer(suppliers, many=True).data)

    def post(self, request):
        s = SupplierSerializer(data=request.data, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "supplier": s.data}, status=201)
        return Response({"status": "0", "errors": s.errors}, status=400)


class SupplierDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, workshop):
        try:
            return Supplier.objects.get(pk=pk, workshop=workshop)
        except Supplier.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Supplier not found"}, status=404)
        return Response(SupplierSerializer(obj).data)

    def patch(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Supplier not found"}, status=404)
        s = SupplierSerializer(obj, data=request.data, partial=True, context={'workshop': get_workshop(request)})
        if s.is_valid():
            s.save()
            return Response({"status": "1", "supplier": s.data})
        return Response({"status": "0", "errors": s.errors}, status=400)

    def delete(self, request, pk):
        obj = self._get_object(pk, get_workshop(request))
        if not obj:
            return Response({"status": "0", "message": "Supplier not found"}, status=404)
        obj.delete()
        return Response({"status": "1", "message": "Supplier deleted"})


# ──────────────────────────────────────────
# PURCHASE ORDER
# ──────────────────────────────────────────

class PurchaseOrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workshop = get_workshop(request)
        pos = PurchaseOrder.objects.filter(
            workshop=workshop
        ).select_related('supplier').prefetch_related('items')

        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            pos = pos.filter(status=status_filter.upper())

        return Response(
            PurchaseOrderSerializer(pos, many=True, context={'workshop': workshop, 'request': request}).data
        )

    def post(self, request):
        workshop = get_workshop(request)
        s = PurchaseOrderSerializer(
            data=request.data,
            context={'workshop': workshop, 'request': request}
        )
        if s.is_valid():
            po = s.save()
            return Response({
                "status": "1",
                "message": "Purchase order created",
                "po_number": po.po_number,
                "po": PurchaseOrderSerializer(po, context={'workshop': workshop, 'request': request}).data
            }, status=201)
        return Response({"status": "0", "errors": s.errors}, status=400)


class PurchaseOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, workshop):
        try:
            return PurchaseOrder.objects.get(pk=pk, workshop=workshop)
        except PurchaseOrder.DoesNotExist:
            return None

    def get(self, request, pk):
        workshop = get_workshop(request)
        obj = self._get_object(pk, workshop)
        if not obj:
            return Response({"status": "0", "message": "Purchase order not found"}, status=404)
        return Response(PurchaseOrderSerializer(obj, context={'workshop': workshop, 'request': request}).data)


class GRNView(APIView):
    """Receive goods against a Purchase Order."""
    permission_classes = [IsOwnerOrSuperUser]

    def post(self, request, pk):
        workshop = get_workshop(request)
        try:
            po = PurchaseOrder.objects.get(pk=pk, workshop=workshop)
        except PurchaseOrder.DoesNotExist:
            return Response({"status": "0", "message": "Purchase order not found"}, status=404)

        if po.status == 'RECEIVED':
            return Response({"status": "0", "message": "Purchase order already fully received"}, status=400)

        if po.status == 'CANCELLED':
            return Response({"status": "0", "message": "Cannot receive a cancelled order"}, status=400)

        s = GRNSerializer(data=request.data)
        if s.is_valid():
            po = apply_grn(po, s.validated_data['items'], request.user)
            return Response({
                "status": "1",
                "message": "GRN processed",
                "po_status": po.status
            })
        return Response({"status": "0", "errors": s.errors}, status=400)


# ──────────────────────────────────────────
# PRICE HISTORY
# ──────────────────────────────────────────

class PriceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, variant_pk):
        workshop = get_workshop(request)
        # Verify variant belongs to workshop
        if not ProductVariant.objects.filter(pk=variant_pk, workshop=workshop).exists():
            return Response({"status": "0", "message": "Variant not found"}, status=404)

        history = PriceHistory.objects.filter(
            product_variant_id=variant_pk,
            workshop=workshop
        )
        return Response(PriceHistorySerializer(history, many=True).data)
