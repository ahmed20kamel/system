from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField()
    supplier = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/')
    stock = models.IntegerField(default=0)  # Added stock field

    def save(self, *args, **kwargs):
        if not self.pk:  # Checking if it's a new instance
            self.stock = self.quantity  # Initialize stock with quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name