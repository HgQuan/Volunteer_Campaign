from django.db.models.functions import TruncDay
from volunteer.models import *
from django.db.models import Count, Sum
def total_revenue_by_day(start_date, end_date):
    orders = Order.objects.filter(active=True, status='SUCCESS', created_date__range=[start_date, end_date])\
        .annotate(day=TruncDay('created_date')).values('day').annotate(total_revenue=Sum('total_price')).order_by('day')
    for item in orders:
        item['day'] = item['day'].isoformat()

    return orders

def count_products_by_category():
    categories = Category.objects.filter(active=True)

    count_products_by_category = categories.values('name').annotate(total_product=Count('products_cate')).order_by('total_product')

    return count_products_by_category

def total_user():
    return User.objects.filter(is_active=True).count()

def total_order_pending():
    return Order.objects.filter(active=True, status='PENDING').count()

def total_product():
    return Product.objects.filter(active=True).count()

def total_revenue():
    return Order.objects.filter(active=True, status='SUCCESS').aggregate(total=Sum('total_price'))['total']

def total_campaign():
    return Campaign.objects.filter(active=True).count()


def total_donation_by_campaign():
    campaigns = Campaign.objects.annotate(total_donation=Sum('donations__money')).values('name', 'total_donation')

    return campaigns


def top_10_donors_by_campaign():
    top_donors = Donation.objects.filter(type=Donation.MONEY) \
                     .values('campaign__name', 'user__username') \
                     .annotate(total_donation=Sum('money')) \
                     .order_by('campaign', '-total_donation')[:10]

    return top_donors

def top_10_products_by_sales():
    return Product.objects.filter(order_product__order__status='SUCCESS')\
                          .annotate(total_sales=Sum('order_product__quantity'))\
                          .order_by('-total_sales')[:10]

def top_10_products_by_likes():
    top_products_by_likes = Product.objects.filter(like__isnull=False).annotate(total_likes=Count('like')).order_by('-total_likes')[:10]
    return top_products_by_likes