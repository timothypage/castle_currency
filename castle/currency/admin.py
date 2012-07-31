# -*- coding: utf-8 -*
from django.contrib import admin

from models import Currency, ExchangeRate, QuarterlyExchangeRate


class ExchangeRateAdmin(admin.ModelAdmin):
    """
    """
    list_filter = ('currency', 'date')
    ordering = ('-date',)


class QuarterlyExchangeRateAdmin(admin.ModelAdmin):
    """
    """
    list_filter = ('currency', 'date')
    ordering = ('-date',)


admin.site.register(Currency)
admin.site.register(ExchangeRate, ExchangeRateAdmin)
admin.site.register(QuarterlyExchangeRate, QuarterlyExchangeRateAdmin)