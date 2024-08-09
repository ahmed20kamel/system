from django.shortcuts import render, redirect
from .models import Product
from django.forms import ModelForm

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'code', 'quantity', 'supplier', 'image']

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/products_list.html', {'products': products})

def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'products/products_form.html', {'form': form})

def product_update(request, id):
    product = Product.objects.get(id=id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'products/products_form.html', {'form': form})

def product_delete(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'products/products_confirm_delete.html', {'object': product})