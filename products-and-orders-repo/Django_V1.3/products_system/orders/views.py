from django.shortcuts import render, redirect, get_object_or_404
from .models import Order
from products.models import Product
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
import datetime
from django.utils import timezone
from django.http import JsonResponse

class OrderForm(ModelForm):
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
    
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    print(f"Total orders in database: {Order.objects.count()}")
    print(f"Orders being sent to template: {len(orders)}")
    return render(request, 'orders/orders_list.html', {'orders': orders})

def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_date = timezone.now()
            product_name = form.cleaned_data['product_name']
            product_code = form.cleaned_data['product_code']
            try:
                product = Product.objects.get(name=product_name, code=product_code)
                if order.quantity <= product.stock:
                    product.stock -= order.quantity
                    product.save()
                    order.save()
                    return redirect('order_list')
                else:
                    form.add_error('quantity', f"Only {product.stock} available. Cannot order more than that.")
            except Product.DoesNotExist:
                form.add_error(None, "Product not found. Please enter a valid product name and code.")
    else:
        form = OrderForm(initial={'due_date': timezone.now().date()})
    return render(request, 'orders/orders_form.html', {'form': form})

def order_update(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'orders/orders_form.html', {'form': form})

def order_delete(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')
    return render(request, 'orders/orders_confirm_delete.html', {'object': order})

def order_approve(request, id):
    order = get_object_or_404(Order, id=id)
    order.status = 'approved'
    order.save()
    return redirect('order_list')

def order_disapprove(request, id):
    order = get_object_or_404(Order, id=id)
    order.status = 'disapproved'
    order.save()
    return redirect('order_list')

def product_search(request):
    term = request.GET.get('term', '')
    field = request.GET.get('field', 'name')
    if field == 'name':
        products = Product.objects.filter(name__icontains=term)[:10]
    else:
        products = Product.objects.filter(code__icontains=term)[:10]
    results = [{'label': f"{p.name} ({p.code})", 'value': p.id, 'name': p.name, 'code': p.code} for p in products]
    return JsonResponse(results, safe=False)