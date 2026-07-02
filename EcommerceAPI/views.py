from itertools import product
from pickle import FALSE
from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filter_fields = ['category','price']
    search_fields = ['name']
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Review.objects.all()
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    @action(detail=False , methods=['get'])
    def my_cart(self, request):
        cart,_ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    @action(detail=False , methods=['post'])
    def add_item(self, request):
        cart,_ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity',1)
        product = Product.objects.get(id=product_id)
        item,created = CartItem.objects.get_or_create(
            cart = cart,
            product = product,
            defaults={'quantity':quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return Response({'status':'product added'})
    @action(detail=False , methods=['post'])
    def checkout(self, request):
        cart = Cart.objects.get(user=request.user)
        total = sum(item.product.price*item.quantity for item in cart.items.all())
        order = Order.objects.create(user=request.user,total_price=total,status = 'pending')
        for item in cart.items.all():
            OrderItem.objects.create(order=order,product=item.product,quantity=item.quantity,price=item.product.price)
        cart.items.all().delete()
        return Response({'status':'order created','order_id':order.id})
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


