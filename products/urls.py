from django.urls import path
from .views import *


urlpatterns = [
    path('brands/', BrandView.as_view(), name= 'list-create-brands'),
    path('brands/<int:id>/', BrandRetrieveUpdateDestroyView.as_view(), name= 'retrieve-update-destroy-brands'),
    
    path('category/', CategoryView.as_view(), name= 'list-create-category'),
    path('category/<int:id>/', CategoryRetrieveUpdateDestroyView.as_view(), name= 'retrieve-update-destroy-category'),
]
