# -*- coding: utf-8 -*
import datetime

from django.test import TestCase

from currency.models import Currency, ExchangeRate, QuarterlyExchangeRate


class ModelTest(TestCase):
    """
    Basic tests of the currency models.
    """
    def test_currency(self):
        """
        """
        us = Currency(
            name="United States",
            abbrev="US",
            pre="$"
        )
        unicode(us) # If the unicode magic method has an error, this will fail
        us.save()
        unicode(us)

        # The is_active attribute should default to False
        self.assertEqual(us.is_active, False)

        # TODO perform an actual count
        self.assertTrue(Currency.objects.all().count())


    def test_exchange_rate(self):
        """
        """
        us = Currency.objects.create(name="United States", abbrev="US")
        us_q1 = ExchangeRate(
            currency=us,
            date=datetime.date(2012, 3, 31),
            rate=1.0
        )
        unicode(us_q1)
        us_q1.save()
        unicode(us_q1)

        # TODO test invalid values, duplicates