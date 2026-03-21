from django.db import models

# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class VehicleBrand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    brand = models.ForeignKey(VehicleBrand, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ['brand', 'model_name']

    def __str__(self):
        return f"{self.brand.name} {self.model_name}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, default="piece")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'category']

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    variant_name = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    compatible_vehicles = models.ManyToManyField(VehicleModel, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'brand', 'variant_name']

    def __str__(self):
        return f"{self.product.name} - {self.brand.name} - {self.variant_name or 'Standard'}"

# class Attribute(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

# class AttributeValue(models.Model):
#     attribute = models.ForeignKey(
#         Attribute,
#         on_delete=models.CASCADE,
#         related_name="values"
#     )

#     value = models.CharField(max_length=100)

#     class Meta:
#         unique_together = ['attribute', 'value']

#     def __str__(self):
#         return f"{self.attribute.name} - {self.value}"
    

# class VariantAttribute(models.Model):

#     product_variant = models.ForeignKey(
#         ProductVariant,
#         on_delete=models.CASCADE,
#         related_name="attributes"
#     )

#     attribute = models.ForeignKey(
#         Attribute,
#         on_delete=models.CASCADE
#     )

#     value = models.ForeignKey(
#         AttributeValue,
#         on_delete=models.CASCADE
#     )

#     class Meta:
#         unique_together = ['product_variant', 'attribute']

#     def __str__(self):
#         return f"{self.product_variant} - {self.attribute.name}:{self.value.value}"
    


# class Supplier(models.Model):
#     name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=20, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name
    

# class Purchase(models.Model):
#     supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
#     purchase_date = models.DateField()
#     total_amount = models.DecimalField(max_digits=12, decimal_places=2)

#     created_at = models.DateTimeField(auto_now_add=True)


# class PurchaseItem(models.Model):
#     purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
#     product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)

#     quantity = models.IntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     subtotal = models.DecimalField(max_digits=12, decimal_places=2)

# class Customer(models.Model):
#     name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=20)
#     vehicle_number = models.CharField(max_length=50, blank=True, null=True)

#     def __str__(self):
#         return self.name
    
# class Sale(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)

#     sale_date = models.DateTimeField(auto_now_add=True)

#     total_amount = models.DecimalField(max_digits=12, decimal_places=2)

#     discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


# class SaleItem(models.Model):
#     sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")

#     product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)

#     quantity = models.IntegerField()

#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     subtotal = models.DecimalField(max_digits=12, decimal_places=2)



# class StockTransaction(models.Model):

#     TRANSACTION_TYPE = (
#         ("purchase", "Purchase"),
#         ("sale", "Sale"),
#         ("adjustment", "Adjustment"),
#         ("return", "Return"),
#     )

#     product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

#     transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)

#     quantity = models.IntegerField()

#     reference_id = models.CharField(max_length=100, blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.product_variant} - {self.transaction_type} - {self.quantity}"
    


# class JobCard(models.Model):

#     STATUS = (
#         ("pending", "Pending"),
#         ("in_progress", "In Progress"),
#         ("completed", "Completed"),
#         ("delivered", "Delivered"),
#     )

#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

#     vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.SET_NULL, null=True)

#     vehicle_number = models.CharField(max_length=50)

#     complaint = models.TextField()

#     status = models.CharField(max_length=20, choices=STATUS, default="pending")

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"JobCard {self.id} - {self.vehicle_number}"
    

# class JobCardItem(models.Model):

#     job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name="items")

#     product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)

#     quantity = models.IntegerField()

#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     subtotal = models.DecimalField(max_digits=12, decimal_places=2)