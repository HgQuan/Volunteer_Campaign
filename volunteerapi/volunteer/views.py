# from django.shortcuts import render
from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from volunteer.models import Category, Product, ProductComment, ProductRating, User, Like, Donation, Order, Campaign, \
    OrderDetail, Cart, CartItem
from volunteer import serializers, paginators, perms
import volunteer.models
from rest_framework.generics import get_object_or_404
from django.db.models import Sum
from paypalrestsdk import Payment
from django.conf import settings
import paypalrestsdk
import logging
from rest_framework.views import APIView
from django.contrib.auth.models import AnonymousUser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox hoặc live cho môi trường production
    "client_id": "AU2F14M5fgAunODLfDultP3_fh5B2b0dXjFtKafC_xU0WPxqZnyZSx7VVN-RFcVeq6j8pyRdvAwd1UJV",
    "client_secret": "EIl_7Sy_AoyBdBuYPNNn8x7_fCa6csfddkokUIuKvcfPu5sbZZqJcz6k_v366Bk2h6HRmx-63vjcuc_W"
})

# Create your views here.
class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer

    @action(methods=['get'], url_path='products', detail=True)
    def get_products(self, request, pk):
        products = self.get_object().products_cate.filter(active=True)
        return Response(serializers.ProductSerializer(products, many=True).data)

class ProductViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                     generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = serializers.ProductDetailSerializer
    pagination_class = paginators.ProductPaginator
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, active=False)

    def get_queryset(self):
        queryset = self.queryset
        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            cate_id = self.request.query_params.get('category_id')
            if cate_id:
                queryset = queryset.filter(category_id=cate_id)

        return queryset

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return serializers.AuthenticatedProductDetailSerializer
        return self.serializer_class

    @action(methods=['get'], url_path='comments', detail=True)
    def get_productcomments(self, request, pk):
        comments = self.get_object().productcomment_set.select_related('user').order_by('-id')
        paginator = paginators.ReviewPaginator()

        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = serializers.ProductCommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

    @action(methods=['post'], url_path='add-comment', detail=True)
    def add_productcomment(self, request, pk):
        parent_id = request.data.copy().get('parent')
        if parent_id:
            parent = ProductComment.objects.get(id=parent_id)
        else:
            parent = None

        c = self.get_object().productcomment_set.create(content=request.data.get('content'), user=request.user,
                                                        parent=parent)
        return Response(serializers.ProductCommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='ratings', detail=True)
    def get_productratings(self, request, pk):
        ratings = self.get_object().productrating_set.select_related('user').order_by('-id')
        paginator = paginators.ReviewPaginator()

        page = paginator.paginate_queryset(ratings, request)
        if page is not None:
            serializer = serializers.ProductRatingSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializers.ProductRatingSerializer(ratings, many=True).data)

    @action(methods=['post'], url_path='add-rating', detail=True)
    def add_productrating(self, request, pk):
        c = self.get_object().productrating_set.create(rating=request.data.get('rating'), user=request.user)
        return Response(serializers.ProductRatingSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        li, created = Like.objects.get_or_create(product=self.get_object(), user=request.user)
        if not created:
            li.active = not li.active
            li.save()

        product = self.get_object()
        serializer = serializers.AuthenticatedProductDetailSerializer(product, context={'request': request})

        data = serializer.data
        data.pop('liked', None)

        return Response(data)

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['get_current_user']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):

            for k, v in request.data.items():
                setattr(user, k, v)
            user.save()
        return Response(serializers.UserSerializer(user).data)

    @action(methods=['get'], url_path='orders', detail=True)
    def get_orders(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        orders = user.order_user.order_by('-id')
        paginator = paginators.OrderPaginator()

        page = paginator.paginate_queryset(orders, request)
        if page is not None:
            serializer = serializers.OrderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializers.OrderSerializer(orders, many=True).data)


class ProductCommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = ProductComment.objects.filter(active=True)
    serializer_class = serializers.ProductCommentSerializer
    permission_classes = [perms.CommentOwner]

class ProductRatingViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = ProductRating.objects.filter(active=True)
    serializer_class = serializers.ProductRatingSerializer
    permission_classes = [perms.RatingOwner]

class DonationViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Donation.objects.all()
    serializer_class = serializers.DonationSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @action(detail=True, methods=['get'], url_path='top-donors')
    def top_donors(self, request, pk=None):
        try:
            campaign = Campaign.objects.get(pk=pk)
        except Campaign.DoesNotExist:
            return Response({"error": "Campaign not found"}, status=404)

        top_donors = Donation.objects.filter(campaign=campaign, type=Donation.MONEY) \
                         .values('user__username') \
                         .annotate(total_donation=Sum('money')) \
                         .order_by('-total_donation')[:10]

        return Response(top_donors)

class OrderViewSet(viewsets.ViewSet, generics.GenericAPIView):
    queryset = Order.objects.filter(active=True)
    serializer_class = serializers.OrderSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status1 = request.data.get('status')
        if status1 not in dict(volunteer.models.STATUS_ORDER_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = status1
        order.save()
        return Response(serializers.OrderSerializer(order).data)

class CampaignViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Campaign.objects.all()
    serializer_class = serializers.CampaignSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

        return queryset

class CartViewSet(viewsets.ViewSet, generics.GenericAPIView):
    queryset = Cart.objects.all()
    serializer_class = serializers.CartSerializer
    permission_classes = [perms.CartOwner]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        return Response(serializers.CartSerializer(cart).data)

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        return Response(serializers.CartSerializer(cart).data)

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)

        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.quantity = int(quantity)
        cart_item.save()

        return Response(serializers.CartSerializer(cart).data)

    @action(detail=True, methods=['post'])
    def select_item(self, request, pk):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        # selected = request.data.get('selected', True)

        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        if cart_item.selected:
            cart_item.selected = False
        else:
            cart_item.selected = True
        # cart_item.selected = selected
        cart_item.save()

        return Response(serializers.CartSerializer(cart).data)

    @action(methods=['post'], detail=True)
    def check_out(self, request, pk=None):
        cart = self.get_object()
        selected_items = cart.items.filter(selected=True)

        if not selected_items.exists():
            return Response({'error': 'Không có sản phẩm nào được chọn để thanh toán'},
                            status=status.HTTP_400_BAD_REQUEST)

        orders = []
        total_price = 0

        order = Order.objects.create(user=request.user)

        for item in selected_items:
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            total_price += item.quantity * item.product.price

            item.delete()

        order.total_price = total_price
        order.save()

        order_serializer = serializers.OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

class CartItemViewSet(viewsets.ViewSet, generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = serializers.CartItemSerializer
    permission_classes = [perms.CartItemOwner]

class PayPalPaymentView(APIView):
    def get_cart(self):
        if isinstance(self.request.user, AnonymousUser):
            return Response({'error': 'Người dùng chưa đăng nhập. Vui lòng đăng nhập để tiếp tục.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            cart = Cart.objects.filter(user=self.request.user).order_by('-created_at').first()

            if not cart:
                return Response({'error': 'Không tìm thấy giỏ hàng của người dùng'}, status=status.HTTP_404_NOT_FOUND)

            return cart

        except Cart.DoesNotExist:
            return Response({'error': 'Giỏ hàng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        cart = self.get_cart()
        if isinstance(cart, Response):
            return cart

        selected_items = cart.items.filter(selected=True)

        if not selected_items.exists():
            return Response({'error': 'Không có sản phẩm nào được chọn để thanh toán'},
                            status=status.HTTP_400_BAD_REQUEST)

        if hasattr(cart, 'status') and cart.status == 'paid':
            return Response({'error': 'Giỏ hàng này đã được thanh toán. Vui lòng tạo giỏ hàng mới để thanh toán lại.'},
                            status=status.HTTP_400_BAD_REQUEST)

        orders = []
        total_price = 0

        order = Order.objects.create(user=request.user)

        for item in selected_items:
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            total_price += item.quantity * item.product.price

            item.delete()

        total_price_str = "{:.2f}".format(total_price)

        order.total_price = total_price
        order.save()

        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": total_price_str,
                    "currency": "USD"
                },
                "description": f"Thanh toán đơn hàng #{order.id}"
            }],
            "redirect_urls": {
                "return_url": "http://localhost:3000/paypal/return",
                "cancel_url": "http://localhost:3000/paypal/cancel"
            }
        })

        if payment.create():
            order.payment_id = payment.id
            order.save()

            approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
            return Response({
                "order_id": order.id,
                "approval_url": approval_url
            }, status=status.HTTP_201_CREATED)
        else:
            logging.error(payment.error)
            return Response({"error": "Payment creation failed"}, status=500)


class PayPalExecuteView(APIView):
    def get(self, request):
        payment_id = request.GET.get('paymentId')
        token = request.GET.get('token')
        payer_id = request.GET.get('PayerID')

        if not payment_id or not payer_id:
            return Response({"error": "Missing paymentId or PayerID"}, status=400)

        try:
            payment = paypalrestsdk.Payment.find(payment_id)

            if payment.state == 'approved':
                order = Order.objects.get(payment_id=payment_id)
                if order.status != 'PENDING':
                    order.status = 'PENDING'
                    order.save()

                return Response({"status": "Payment already completed"}, status=status.HTTP_200_OK)

            if payment.execute({"payer_id": payer_id}):
                order = Order.objects.get(payment_id=payment_id)
                order.status = 'PENDING'
                order.save()

                return Response({"status": "Thanh toán thành công"}, status=status.HTTP_200_OK)
            else:
                logging.error(payment.error)
                return Response({"error": payment.error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except paypalrestsdk.ResourceNotFound as e:
            logging.error(f"Payment not found: {e}")
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logging.error(f"Exception during PayPal payment execution: {e}")
            return Response({"error": "Something went wrong during payment execution."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
