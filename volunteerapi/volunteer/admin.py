from django.contrib import admin
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from volunteer.models import Category, Product, User, ProductComment, ProductRating, Campaign, Donation, Like, Order, OrderDetail, Cart, CartItem
from django.urls import path
from django.template.response import TemplateResponse
from volunteer import dao
import datetime
from django.db.models import Sum
from oauth2_provider.models import AccessToken, Application, Grant, RefreshToken
# Register your models here.

class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'application', 'expires', 'scope']
    search_fields = ['user__username', 'application__name']

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_id', 'user']
    search_fields = ['name', 'client_id', 'user__username']

class GrantAdmin(admin.ModelAdmin):
    list_display = ['user', 'application', 'code', 'expires']
    search_fields = ['user__username', 'application__name']

class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'application', 'token']
    search_fields = ['user__username', 'application__name']
class ProductForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Product
        fields = '__all__'

class MyProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory_quantity', 'price', 'created_date', 'updated_date', 'active', 'user']
    search_fields = ['name', 'description']
    list_filter = ['id', 'created_date', 'name']
    form = ProductForm
    readonly_fields = ['my_image']

    def my_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="150" />')
        return "No Image"

class MyCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_date', 'updated_date', 'active']
    search_fields = ['name']
    list_filter = ['id', 'created_date', 'name']

class MyUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'is_active']
    search_fields = ['username', 'first_name', 'last_name']
    list_filter = ['id', 'username']
    readonly_fields = ['my_avatar']

    def my_avatar(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="150" height="150" />')
        return "No Image"

class DonationAdminForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DonationAdminForm, self).__init__(*args, **kwargs)
        self.fields['money'].widget.attrs['disabled'] = 'disabled'
        self.fields['product'].widget.attrs['disabled'] = 'disabled'

class DonationAdmin(admin.ModelAdmin):
    form = DonationAdminForm
    list_display = ('campaign', 'type', 'money', 'product')

    class Media:
        js = ('admin/js/donation.js',)

class DetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 1

class MyOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_date', 'updated_date', 'active']
    search_fields = ['user']
    list_filter = ['id', 'user']
    inlines = [DetailInline]

class MyOrderDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity']

class MyCampaignAdmin(admin.ModelAdmin):
    readonly_fields = ['my_image']

    def my_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="150" />')
        return "No Image"

class VolunteerAdminSite(admin.AdminSite):
    site_header = 'VolunteerAdmin'

    def get_urls(self):
        return [path('volunteer-stats/', self.stats_view)] + super().get_urls()

    def stats_view(self, request):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        selected_campaign_id = request.GET.get('campaign_id')

        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            today = datetime.datetime.today()
            start_date = today - datetime.timedelta(days=30)
            end_date = today

        total_revenue_by_day = dao.total_revenue_by_day(start_date, end_date)
        total_buyer = dao.total_user()
        total_order_pending = dao.total_order_pending()
        total_product = dao.total_product()
        total_revenue = dao.total_revenue()
        count_products_by_category = dao.count_products_by_category()
        total_campaign = dao.total_campaign()
        total_donation_by_campaign = dao.total_donation_by_campaign()
        top_10_products = dao.top_10_products_by_sales()
        top_10_products_by_likes = dao.top_10_products_by_likes()

        campaigns = Campaign.objects.all()
        if selected_campaign_id:
            selected_campaign = Campaign.objects.get(id=selected_campaign_id)
            top_donors_by_campaign = Donation.objects.filter(campaign=selected_campaign, type=Donation.MONEY) \
                                         .values('user__username') \
                                         .annotate(total_donation=Sum('money')) \
                                         .order_by('-total_donation')[:10]
            selected_campaign_name = selected_campaign.name
        else:
            top_donors_by_campaign = Donation.objects.filter(type=Donation.MONEY) \
                                         .values('campaign__name', 'user__username') \
                                         .annotate(total_donation=Sum('money')) \
                                         .order_by('campaign__name', '-total_donation')[:10]
            selected_campaign_name = None

        return TemplateResponse(request, 'admin/stats.html',{
            "total_buyer": total_buyer,
            "total_order_pending": total_order_pending,
            "total_product": total_product,
            "total_revenue_by_day": total_revenue_by_day,
            "count_products_by_category": count_products_by_category,
            "total_revenue": total_revenue,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_campaign': total_campaign,
            'campaigns': campaigns,
            'top_donors_by_campaign': top_donors_by_campaign,
            'selected_campaign_id': selected_campaign_id,
            'selected_campaign_name': selected_campaign_name,
            'top_10_products': top_10_products,
            'top_10_products_by_likes': top_10_products_by_likes,
        })

admin_site = VolunteerAdminSite(name='Volunteer')
admin_site.register(Category, MyCategoryAdmin)
admin_site.register(Product, MyProductAdmin)
admin_site.register(User, MyUserAdmin)
admin_site.register(ProductComment)
admin_site.register(ProductRating)
admin_site.register(Campaign, MyCampaignAdmin)
admin_site.register(Donation, DonationAdmin)
admin_site.register(Like)
admin_site.register(Order, MyOrderAdmin)
admin_site.register(OrderDetail, MyOrderDetailAdmin)
admin_site.register(Cart)
admin_site.register(CartItem)
admin_site.register(AccessToken, AccessTokenAdmin)
admin_site.register(Application, ApplicationAdmin)
admin_site.register(Grant, GrantAdmin)
admin_site.register(RefreshToken, RefreshTokenAdmin)