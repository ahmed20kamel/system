from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name', 'quantity', 'status', 'order_date', 'due_date']
    list_filter = ['status']