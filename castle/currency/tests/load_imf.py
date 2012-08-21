# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.core.management.base import CommandError

from currency.management.commands.load_imf import parse_date, parse_exchange_rate, parse_currency, parse_tsv, save_imf
from currency.models import Currency, ExchangeRate

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
        filename = 'currency/tests/testfiles/small.tsv'

        Currency.objects.bulk_create([
            Currency(name="Japanese yen", abbrev="JPY"),
            Currency(name="U.K. pound sterling", abbrev="GBP"),
            Currency(name="U.S. dollar", abbrev="USD")
        ])
        currencies = Currency.objects.in_bulk([1,2,3])
        jpy = currencies[1]
        gbp = currencies[2]
        usd = currencies[3]

        feb1 = datetime.date(2011, 2, 1)
        feb2 = datetime.date(2011, 2, 2)
        feb3 = datetime.date(2011, 2, 3)

        exchange_rates = parse_tsv(filename)
        # GBP is an inverted currency in imf files, so we'll have to invert it here
        # see currency.management.command comments for more details
        expected = {
                (jpy, feb1): 82.02,
                (gbp, feb1): (1/1.611),
                (usd, feb1): 1,
                (jpy, feb2): 81.5,
                (gbp, feb2): (1/1.6202),
                (usd, feb2): 1,
                (jpy, feb3): 81.64,
                (gbp, feb3): (1/1.6215),
                (usd, feb3): 1
        }

        self.assertEqual(exchange_rates, expected)

    def test_save_imf(self):
        Currency.objects.bulk_create([
                Currency(name="Japanese yen", abbrev="JPY"),
                Currency(name="U.K. pound sterling", abbrev="GBP"),
                Currency(name="U.S. dollar", abbrev="USD")
            ])
        currencies = Currency.objects.in_bulk([1,2,3])
        jpy = currencies[1]
        gbp = currencies[2]
        usd = currencies[3]
    
        feb1 = datetime.date(2011, 2, 1)
        feb2 = datetime.date(2011, 2, 2)
        feb3 = datetime.date(2011, 2, 3)

        expected = {
                (jpy, feb1): 82.02,
                (gbp, feb1): 1.611,
                (usd, feb1): 1,
                (jpy, feb2): 81.5,
                (gbp, feb2): 1.6202,
                (usd, feb2): 1,
                (jpy, feb3): 81.64,
                (gbp, feb3): 1.6215,
                (usd, feb3): 1
        }
        save_imf(expected)
        self.assertEqual(len(ExchangeRate.objects.all()), len(expected))
        expected[jpy, feb1] = 123.0
        save_imf(expected)
        database_jpy_feb1 = ExchangeRate.objects.get(currency=jpy, date=feb1)
        self.assertEqual(expected[jpy, feb1], database_jpy_feb1.rate)

    def test_bad_file(self):
        Currency.objects.bulk_create([
                Currency(name="Japanese yen", abbrev="JPY"),
                Currency(name="U.K. pound sterling", abbrev="GBP"),
                Currency(name="U.S. dollar", abbrev="USD")
            ])
        currencies = Currency.objects.in_bulk([1,2,3])
        jpy = currencies[1]
        gbp = currencies[2]
        usd = currencies[3]

        feb1 = datetime.date(2011, 2, 1)
        feb2 = datetime.date(2011, 2, 2)
        feb3 = datetime.date(2011, 2, 3)

        expected = {
                (jpy, feb1): 82.02,
                (gbp, feb1): 1.611,
                (usd, feb1): 1,
                (jpy, feb2): 81.5,
                (gbp, feb2): 1.6202,
                (usd, feb2): 1,
                (jpy, feb3): 81.64,
                (gbp, feb3): 1.6215,
                (usd, feb3): 1
        }
        try:
            parse_tsv('currency/tests/testfiles/mess-with-rr.tsv')
            self.assertTrue(False)
        except CommandError:
            self.assertTrue(True)

        self.assertEqual(expected, parse_tsv('currency/tests/testfiles/mess-with-tabs.tsv'))
