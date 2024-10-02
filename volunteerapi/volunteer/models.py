from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# Create your models here.

class User(AbstractUser):
    avatar = CloudinaryField(null=True)


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Campaign(BaseModel):
    name = models.CharField(max_length=100)
    ended_date = models.DateTimeField(null=True, blank=True)
    description = RichTextField(blank=True, null=True)
    money = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_money = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = CloudinaryField(null=True)

    def update_current_money(self):
        total_money = self.donations.filter(type=Donation.MONEY).aggregate(total=models.Sum('money'))['total'] or 0
        self.current_money = total_money
        self.save()

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=100)
    description = RichTextField(blank=True, null=True)
    inventory_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    image = CloudinaryField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products_cate')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='products')
    donated = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductInteraction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ProductComment(ProductInteraction):
    content = models.CharField(max_length=255)
    parent = models.ForeignKey('ProductComment', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.first_name}"

class ProductRating(ProductInteraction):
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.product.name} - {self.user.first_name} - {self.rating}"

    def clean(self):
        if int(self.rating) < 1 or int(self.rating) > 5:
            raise ValidationError("Rating must be between 1 and 5.")

    class Meta:
        unique_together = ('user', 'product')


class Like(ProductInteraction):

    def __str__(self):
        return f'{self.user_id} - {self.product_id}'

    class Meta:
        unique_together = ('user', 'product')


class Donation(BaseModel):
    MONEY = 'money'
    PRODUCT = 'product'
    DONATION_TYPE_CHOICES = [
        (MONEY, 'Money'),
        (PRODUCT, 'Product'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='donations')
    type = models.CharField(max_length=7, choices=DONATION_TYPE_CHOICES)
    money = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations', null=True, blank=True)

    def clean(self):
        if self.type == self.MONEY and (self.money is None or self.money == 0):
            raise ValidationError("Money donation must include an amount.")
        if self.type == self.PRODUCT and self.product is None:
            raise ValidationError("Product donation must reference a product.")
        if self.type == self.MONEY:
            self.product = None
        if self.type == self.PRODUCT:
            self.money = None

    def __str__(self):
        return f"Donation to {self.campaign.name} ({self.type})"

STATUS_ORDER_CHOICES = (
    ('PENDING', 'pending'),
    ('ONGOING', 'ongoing'),
    ('SUCCESS', 'success'),
    ('ONHOLD', 'onhold')
)

class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='order_user')
    status = models.CharField(max_length=100, choices=STATUS_ORDER_CHOICES, default=STATUS_ORDER_CHOICES[0][0])
    total_price = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} from {self.user.username}: total {self.total_price}"

    def calculate_total_price(self):
        return sum(item.total_price() for item in self.details.all())

    def save(self, *args, **kwargs):
        if self.total_price is None:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


class OrderDetail(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_product')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.product.price
        super().save(*args, **kwargs)

    def total_price(self):
        return self.quantity * self.price

    class Meta:
        unique_together = ('order', 'product')

@receiver(post_save, sender=OrderDetail)
@receiver(post_delete, sender=OrderDetail)
def update_order_total_price(sender, instance, **kwargs):
    order = instance.order
    order.total_price = order.calculate_total_price()
    order.save()

class Cart(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Cart of {self.user.username} - Status: {self.status}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"