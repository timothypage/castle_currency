# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase

from currency.management.commands.load_imf import parse_date, parse_exchange_rate, parse_currency, parse_tsv
from currency.models import Currency

class ParseTest(TestCase):
    """ test parsing of dates """
    def test_date(self):
        """
        """
        # test for the common case
        target_date = datetime.date(2011, 1, 3)
        date_string = "03-Jan-2011"
        self.assertEqual(parse_date(date_string), target_date)
        
        # test for other input
        self.assertEqual(parse_date('\t'), None)
        self.assertEqual(parse_date(''), None)
        self.assertEqual(parse_date(' '), None)
        self.assertEqual(parse_date('1.053'), None)

    def test_parse_exchange_rate(self):
        self.assertEqual(parse_exchange_rate('1.009'), 1.009)
        self.assertEqual(parse_exchange_rate(''), None)
        self.assertEqual(parse_exchange_rate('\t'), None)
        self.assertEqual(parse_exchange_rate("03-Jan-2011"), None)
        
    def test_parse_currency(self):
        Currency.objects.create(name="Australian dollar", abbrev="AUD")
        self.assertEqual(Currency.objects.all().count(), 1)
        self.assertEqual(parse_currency("Australian dollar(AUD)"),
            Currency.objects.get(abbrev="AUD"))
        self.assertEqual(parse_currency("NONSENSE"), None)
        self.assertEqual(parse_currency(""), None)

    def test_parse_tsv(self):
        filename = 'currency/tests/testfiles/historical.tsv'
        Currency.objects.create(name="Australian dollar", abbrev="AUD")
        Currency.objects.create(name="Canadian dollar", abbrev="CAD")
        Currency.objects.create(name="Chinese yuan", abbrev="CNY")
        Currency.objects.create(name="Euro", abbrev="EUR")
        Currency.objects.create(name="Indian rupee", abbrev="INR")
        Currency.objects.create(name="Japanese yen", abbrev="JPY")
        Currency.objects.create(name="Korean won", abbrev="KRW")
        parse_tsv(filename)

