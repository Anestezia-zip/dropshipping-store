import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django_countries.fields import CountryField
from products.models import Product
from profiles.models import UserProfile

class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False, verbose_name='Номер замовлення')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Профіль користувача')
    full_name = models.CharField(max_length=50, null=False, blank=False, verbose_name='Повне ім\'я')
    email = models.EmailField(max_length=254, null=False, blank=False, verbose_name='Електронна пошта')
    phone_number = models.CharField(max_length=20, null=False, blank=False, verbose_name='Номер телефону')
    country = CountryField(blank_label='Країна *', null=False, blank=False, verbose_name='Країна')
    postcode = models.CharField(max_length=20, null=True, blank=True, verbose_name='Поштовий індекс')
    town_or_city = models.CharField(max_length=40, null=False, blank=False, verbose_name='Місто або село')
    street_address1 = models.CharField(max_length=80, null=False, blank=False, verbose_name='Адреса (лінія 1)')
    street_address2 = models.CharField(max_length=80, null=True, blank=True, verbose_name='Адреса (лінія 2)')
    county = models.CharField(max_length=80, null=True, blank=True, verbose_name='Область')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0, verbose_name='Вартість доставки')
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0, verbose_name='Загальна сума замовлення')
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0, verbose_name='Загальна сума')
    original_bag = models.TextField(null=False, blank=False, default='', verbose_name='Оригінальний кошик')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='', verbose_name='Stripe PID')

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            sdp = settings.STANDARD_DELIVERY_PERCENTAGE
            self.delivery_cost = self.order_total * sdp / 100
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems', verbose_name='Замовлення')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE, verbose_name='Продукт')
    product_size = models.CharField(max_length=2, null=True, blank=True, verbose_name='Розмір продукту')  # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0, verbose_name='Кількість')
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False, verbose_name='Сума')

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.product.sku} на замовленні {self.order.order_number}'
