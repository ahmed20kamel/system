from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Order, Product
from django.db.models import Q

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product_name', 'product_code', 'quantity', 'due_date', 'project_name', 'project_code', 'order_name', 'project_phase', 'project_consultant', 'project_location']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs.update({'class': 'autocomplete'})
        self.fields['product_code'].widget.attrs.update({'class': 'autocomplete'})

    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        product_code = cleaned_data.get('product_code')
        if not product_name or not product_code:
            raise ValidationError("Both product name and code are required.")
        try:
            product = Product.objects.get(name=product_name, code=product_code)
        except Product.DoesNotExist:
            raise ValidationError("Product not found. Please enter a valid product name and code.")
        return cleaned_data

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        today = timezone.now().date()
        if due_date and due_date < today:
            raise ValidationError("Due date cannot be in the past.")
        return due_date
    
    def clean_quantity(self):
        product_name = self.cleaned_data.get('product_name')
        product_code = self.cleaned_data.get('product_code')
        quantity = self.cleaned_data.get('quantity')
        try:
            product = Product.objects.get(name=product_name, code=product_code)
            if quantity > product.stock:
                raise ValidationError(f"Only {product.stock} available. Cannot order more than that.")
        except Product.DoesNotExist:
            pass  # This will be handled in the clean method
        return quantity
    
class OrderReviewForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']