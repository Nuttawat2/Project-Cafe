from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.menu_add, name='menu_add'),
    path('menu/edit/<int:pk>/', views.menu_edit, name='menu_edit'),
    path('menu/delete/<int:pk>/', views.menu_delete, name='menu_delete'),
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/add-stock/<int:pk>/', views.add_stock, name='add_stock'),
    path('orders/', views.order_list, name='order_list'),
    path('customer/', views.customer_menu, name='customer_menu'),
    path('customer/order/', views.customer_order, name='customer_order'),
    path('customer/queue/<int:order_id>/', views.customer_queue, name='customer_queue'),
    path('queue/', views.queue_manage, name='queue_manage'),
    path('queue/update/<int:queue_id>/', views.queue_update, name='queue_update'),
    path('queue/clear/', views.queue_clear, name='queue_clear'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/register/', views.customer_register, name='customer_register'),
]