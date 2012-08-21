# -*- coding: utf-8 -*
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from currency.manager import VortexManager

class Currency(models.Model):
    """
    A currency with included format options.
    """
    name = models.CharField(max_length=127)
    abbrev = models.CharField(max_length=3, unique=True)
    symbol = models.CharField(max_length=5, null=True, blank=True)
    pre = models.CharField(max_length=5, null=True, blank=True)
    delimiter = models.CharField(max_length=5)
    fractional = models.CharField(max_length=5)
    post = models.CharField(max_length=5, null=True, blank=True)
    excel = models.CharField(max_length=127, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "currencies"
        verbose_name_plural = "Currencies"


class ExchangeRate(models.Model):
    """
    An exchange rate taken at end of day EST, daily.
    """
    # Index is removed from currency, since there is a unique currency/date
    currency = models.ForeignKey(Currency, db_index=False)
    date = models.DateField()
    rate = models.FloatField()
    modified = models.DateTimeField(auto_now=True)

    objects = VortexManager()
    
    def clean(self):
        if self.rate <= 0.0:
            raise ValidationError("An exchange rate must be greater than zero")
    
    # def save(self, *args, **kwargs):
    #     super(ExchangeRate, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u"{name} ({date}): {rate}".format(
            name=self.currency.name,
            date=self.date,
            rate=self.rate
        )
    
    class Meta:
        db_table = "exchange_rates"
        unique_together = (("currency", "date"),)
        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"
        

class QuarterlyExchangeRate(models.Model):
    """
    The average exchange rate for the quarter
    """
    # Index is removed from currency, since there is a unique currency/date
    currency = models.ForeignKey(Currency, db_index=False)
    date = models.DateField() # TODO should be a quarter field
    rate = models.FloatField()
    modified = models.DateTimeField(auto_now=True)
    
    def clean(self):
        # TODO validator?
        if self.rate <= 0.0:
            raise ValidationError("An exchange rate must be greater than zero")
    
    def __unicode__(self):
        # TODO should display the quarter
        return u"{name} ({date}): {rate}".format(
            name=self.currency.name,
            date=self.date,
            rate=self.rate
        )
    
    class Meta:
        db_table = "quarterly_exchange_rates"
        unique_together = (("currency", "date"),)
        verbose_name = "Quarterly Exchange Rate"
        verbose_name_plural = "Quarterly Exchange Rates"
        
