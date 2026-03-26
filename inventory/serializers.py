from rest_framework import serializers
from .models import *



class BrandSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields =[
            'id',
            'name',
            'description',
            'created_at'
        ]


class CategorySerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields =[
            'id',
            'name',
            'description',
            'created_at'
        ]

class VehicleBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleBrand
        fields = '__all__'


class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = '__all__'


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'