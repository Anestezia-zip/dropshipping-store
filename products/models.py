from django.db import models


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Категорії'

    name = models.CharField(max_length=254, verbose_name='Назва')
    friendly_name = models.CharField(max_length=254, null=True, blank=True, verbose_name='Дружня назва')

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Категорія')
    sku = models.CharField(max_length=254, null=True, blank=True, verbose_name='Артикул')
    name = models.CharField(max_length=254, verbose_name='Назва')
    description = models.TextField(verbose_name='Опис')
    has_sizes = models.BooleanField(default=False, null=True, blank=True, verbose_name='Має розміри?')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Ціна')
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Рейтинг')
    image_url = models.URLField(max_length=1024, null=True, blank=True, verbose_name='URL зображення')
    image = models.ImageField(null=True, blank=True, verbose_name='Зображення')

    def __str__(self):
        return self.name
