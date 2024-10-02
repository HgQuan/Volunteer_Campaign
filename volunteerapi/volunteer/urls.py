from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from volunteer import views
from .views import PayPalPaymentView

r = routers.DefaultRouter()
r.register('categories', views.CategoryViewSet, 'categories')
r.register('products', views.ProductViewSet, 'products')
r.register('users', views.UserViewSet, 'users')
r.register('productcomments', views.ProductCommentViewSet, 'productcomments')
r.register('productratings', views.ProductRatingViewSet, 'productratings')
r.register('donations', views.DonationViewSet, 'donations')
r.register('orders', views.OrderViewSet, 'orders')
r.register('campaigns', views.CampaignViewSet, 'campaigns')
r.register('carts', views.CartViewSet, 'cars')
r.register('cartitems', views.CartItemViewSet, 'cartitems')

urlpatterns = [
    path('execute-payment/', views.PayPalExecuteView.as_view(), name='execute-payment'),
    path('create-payment/', views.PayPalPaymentView.as_view(), name='create-payment'),
    path('', include(r.urls)),
]
