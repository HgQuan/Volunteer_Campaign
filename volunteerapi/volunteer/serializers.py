from rest_framework import serializers
from volunteer.models import Category, Product, ProductComment, ProductRating, User, Campaign, Donation, Order, OrderDetail, Cart, CartItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        else:
            rep['image'] = None
        return rep

class ProductSerializer(ItemSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'category', 'donated']

class ProductDetailSerializer(ProductSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    class Meta:
        model = ProductSerializer.Meta.model
        fields = ProductSerializer.Meta.fields + ['description', 'inventory_quantity', 'campaign', 'user_id', 'donated', 'active']

class AuthenticatedProductDetailSerializer(ProductDetailSerializer):
    liked = serializers.SerializerMethodField()
    def get_liked(self, product):
        user = self.context['request'].user
        if user.is_authenticated:
            return product.like_set.filter(user=user, active=True).exists()
        return False

    class Meta:
        model = ProductDetailSerializer.Meta.model
        fields = ProductDetailSerializer.Meta.fields + ['liked']

class CampaignSerializer(ItemSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    money = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Donation
        fields = ['id', 'campaign', 'type', 'money', 'product', 'user']

    def validate(self, data):
        if data['type'] == Donation.MONEY and data.get('money') is None:
            raise serializers.ValidationError("Money donation must include an amount.")
        if data['type'] == Donation.PRODUCT and data.get('product') is None:
            raise serializers.ValidationError("Product donation must reference a product.")
        return data

class UserSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.avatar:
            rep['avatar'] = instance.avatar.url
        else:
            rep['avatar'] = None
        return rep

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data["password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'avatar': {'required': False}
        }

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

class ProductCommentSerializer(CommentSerializer):

    def get_parent(self, obj):
        if obj.parent:
            parent = ProductComment.objects.get(pk=obj.parent.id)
            serializer = ProductCommentSerializer(parent)
            return serializer.data
        else:
            return None
    class Meta:
        model = ProductComment
        fields = ['id', 'content', 'created_date', 'updated_date', 'user', 'product', 'parent']

class ProductRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = ProductRating
        fields = ['id', 'rating', 'created_date', 'updated_date', 'user', 'product']

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(many=True, read_only=True)
    user = UserSerializer()
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['total_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
