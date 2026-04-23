"""
inventory/urls.py
"""

from django.urls import path
from inventory.views import (
    BrandListCreateView, BrandDetailView,
    CategoryListCreateView, CategoryDetailView,
    ProductListCreateView, ProductDetailView,
    ProductVariantListCreateView, ProductVariantDetailView,
    StockListView, StockAdjustView,
    StockAlertListCreateView,
    SupplierListCreateView, SupplierDetailView,
    PurchaseOrderListCreateView, PurchaseOrderDetailView, GRNView,
    PriceHistoryView,
)

urlpatterns = [

    # Brand
    path('brands/',          BrandListCreateView.as_view(), name='brand-list'),
    path('brands/<int:pk>/', BrandDetailView.as_view(),     name='brand-detail'),

    # Category
    path('categories/',          CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(),     name='category-detail'),

    # Product
    path('products/',          ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(),     name='product-detail'),

    # Product Variant
    path('variants/',          ProductVariantListCreateView.as_view(), name='variant-list'),
    path('variants/<int:pk>/', ProductVariantDetailView.as_view(),     name='variant-detail'),

    # Stock
    path('stock/',         StockListView.as_view(),   name='stock-list'),
    path('stock/adjust/',  StockAdjustView.as_view(), name='stock-adjust'),

    # Stock Alert
    path('stock/alerts/', StockAlertListCreateView.as_view(), name='stock-alert-list'),

    # Supplier
    path('suppliers/',          SupplierListCreateView.as_view(), name='supplier-list'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(),     name='supplier-detail'),

    # Purchase Order
    path('purchase-orders/',             PurchaseOrderListCreateView.as_view(), name='po-list'),
    path('purchase-orders/<int:pk>/',    PurchaseOrderDetailView.as_view(),     name='po-detail'),
    path('purchase-orders/<int:pk>/grn/', GRNView.as_view(),                   name='po-grn'),

    # Price History
    path('variants/<int:variant_pk>/price-history/', PriceHistoryView.as_view(), name='price-history'),
]
