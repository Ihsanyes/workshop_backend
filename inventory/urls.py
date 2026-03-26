from django.urls import path
from .views import *


urlpatterns = [
    path('brands/', BrandView.as_view(), name= 'list-create-brands'),
    path('brands/<int:id>/', BrandRetrieveUpdateDestroyView.as_view(), name= 'retrieve-update-destroy-brands'),
    
    path('category/', CategoryView.as_view(), name= 'list-create-category'),
    path('category/<int:id>/', CategoryRetrieveUpdateDestroyView.as_view(), name= 'retrieve-update-destroy-category'),

    path('vehicle-brands/', VehicleBrandListCreateView.as_view(), name='vehicle-brand-list-create'),
    path('vehicle-brands/<int:pk>/', VehicleBrandDetailView.as_view(), name='vehicle-brand-detail'),

    path('vehicle-models/', VehicleModelListCreateView.as_view(), name='vehicle-model-list-create'),
    path('vehicle-models/<int:pk>/', VehicleModelDetailView.as_view(), name='vehicle-model-detail'),
]
