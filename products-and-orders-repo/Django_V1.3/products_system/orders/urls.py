from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('new/', views.order_create, name='order_new'),
    path('edit/<int:id>/', views.order_update, name='order_edit'),
    path('delete/<int:id>/', views.order_delete, name='order_delete'),
    path('approve/<int:id>/', views.order_approve, name='order_approve'),
    path('disapprove/<int:id>/', views.order_disapprove, name='order_disapprove'),
    path('product-search/', views.product_search, name='product_search'),
]