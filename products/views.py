from django.shortcuts import render
from rest_framework import generics, status
from .serializers import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from users.permission import HasModulePermission, IsAdminOrSuperUser
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.


class BrandView(APIView):
    def post(self, request):
        serializer = BrandSerilaizer(data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(
            {"status": "1", "message": "success", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
        
    def get(self, request):
        brands = Brand.objects.all()
        serializer = BrandSerilaizer(brands, many=True)
        return Response(
            {"status": "1", "message": "success", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )


class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = BrandSerilaizer
    queryset = Brand.objects.all()
    lookup_field = "id"