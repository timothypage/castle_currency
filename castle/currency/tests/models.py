# -*- coding: utf-8 -*
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

        # The is_active attribute should default to False
        self.assertEqual(us.is_active, False)

        # TODO perform an actual count
        self.assertTrue(Currency.objects.all().count())