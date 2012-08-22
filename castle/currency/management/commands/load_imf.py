# -*- coding: utf-8 -*-
from __future__ import print_function
import csv
import datetime
from difflib import SequenceMatcher
import re
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Avg

from currency.models import Currency, ExchangeRate, QuarterlyExchangeRate
from currency.updates import bulk_update
from castle import quarters


def fuzzy_matcher(string1, string2):
    """ return a string match score: """
    return SequenceMatcher(None, string1, string2).ratio()

"""
Historical IMF data can be queried through: http://www.imf.org/external/np/fin/ert/GUI/Pages/CountryDataBase.aspx

Use currencies / representative rates

Main report page: http://www.imf.org/external/np/fin/data/param_rms_mth.aspx

Daily rates for the iMF are located at: http://www.imf.org/external/np/fin/data/rms_rep.aspx

With a tsv report: http://www.imf.org/external/np/fin/data/rms_rep.aspx?tsvflag=Y

Currencies that require inversion:
    - EUR
    - GBP
    - AUD
    - NZD
"""

def ask_boolean(message):
    """
    Standard yes / no query for command line input
    """
    affirms = set(['y', 'yes', 'true', 't', '1', 'sure', 'okay'])
    negs = set(['n', 'no', 'false', 'f', '0', 'nope', 'cancel'])
    answer = (raw_input(message)).lower()
    
    # TODO stack depth?
    
    if answer in affirms:
        return True
    elif answer in negs:
        return False
    else:
        print(" > please answer 'yes' or 'no'")
        return ask_boolean(message)


def parse_date(date_string):
    """ each line will start with date to be parsed to python datetime object,
        return None if parsing fails"""
    try:
        return datetime.datetime.strptime(date_string, "%d-%b-%Y").date()
    except ValueError:
        pass
    return None


def parse_exchange_rate(exchange_string):
    try:
        return float(exchange_string.replace("\xa0", ""))
    except ValueError:
        pass
    return None


def parse_currency(currency_string):
    p = re.compile('\([A-Z]{3}\)') # exactly three upper case letters inside parentheses
    try:
        abbrev_string = p.search(currency_string).group()
        abbrev_string = abbrev_string.strip('()')
    except AttributeError:
        return None

    try:
        return Currency.objects.get(abbrev=abbrev_string)
    except Currency.DoesNotExist:
        pass
    return None


def parse_tsv(filename):
#    import pdb; pdb.set_trace()
    currency_lookup = {}
    exchange_rates = {}
    pivot = None

    with open(filename, 'r') as f:
        imf = csv.reader(f, delimiter='\t')

        for row_number, row in enumerate(imf):
            for col_number, col in enumerate(row):
                if col[:20] == "Representative rates":
                    pivot = (row_number, col_number)
                    break
            if pivot:
                break
        if not pivot:
            raise CommandError("Couldn't find the phrase 'Representative Rates'; Pivot point not set")

        currency_row = imf.next()
        for col, currency_string in enumerate(currency_row):
            parsed_currency = parse_currency(currency_string)
            if parsed_currency:
                currency_lookup[col] = parsed_currency

        if not currency_lookup:
            raise CommandError("Didn't parse any currencies from the file")

        for row, line in enumerate(imf):
            if len(line) < 2:
                continue

            exchange_rate_date = parse_date(line[pivot[1]])
            if not exchange_rate_date:
                continue

            offset = pivot[1] + 1 # move past date col
            for col, exchange_rate in enumerate(line[offset:]):
                true_col = col + offset
                if not true_col in currency_lookup:
                    continue
                parsed_exchange_rate = parse_exchange_rate(exchange_rate)
                if parsed_exchange_rate:
                    if currency_lookup[true_col].abbrev in ["EUR", "GBP", "AUD", "NZD"]:
                        parsed_exchange_rate = 1/parsed_exchange_rate
                    exchange_rates[(currency_lookup[true_col], exchange_rate_date)] = parsed_exchange_rate


    return exchange_rates

def save_imf(exchange_rates):
    """
    save exchange rate dictionary as ExchangeRate object in the database
    TODO: generalize later
    TODO: save in a transaction? optimize saves?
    """
    for key, rate in exchange_rates.items():
        currency, date = key

        exchange_rate = None
        try:
            exchange_rate = ExchangeRate.objects.get(currency=currency, date=date)
        except ExchangeRate.DoesNotExist:
            ExchangeRate(currency=currency, date=date, rate=rate).save()

        if exchange_rate:
            if exchange_rate.rate == rate:
                continue

            exchange_rate.rate = rate
            exchange_rate.save()

def which_quarter(date):
    """
    Return a tuple (integer 1-4 quarter, integer year) corresponding to which quarter date is in
    """

    year = date.year

    if date.month <= 3:
        quarter = (3, 31)

    elif date.month <= 6:
        quarter = (6, 30)

    elif date.month <= 9:
        quarter = (9, 30)

    elif date.month <= 12:
        quarter = (12, 31)

    return (datetime.date(year, quarter[0], quarter[1]))

def begin_quarter(date):
    """
    returns the beginning date of a quarter given a date
    """
    year = date.year
    if date.month <= 3:
        begin_date = (1, 1)

    elif date.month <= 6:
        begin_date = (4, 1)

    elif date.month <= 9:
        begin_date = (7, 1)

    elif date.month <= 12:
        begin_date = (10, 1)

    return (datetime.date(year, begin_date[0], begin_date[1]))


def calc_quarterly_exchange_rates(exchange_rates):
    """
    calculates the quarterly exchange rates for a list of currencies.
    """
    currencies = set()
    quarters = set()
    quarterly_exchange_rates = {}
    for currency, date in exchange_rates.keys():
        currencies.add(currency)
        quarters.add(which_quarter(date))

    for currency in currencies:
        for quarter in quarters:
            # select all ExchangeRates over the date range for that currency
            quarter_rate = ExchangeRate.objects.filter(
                        currency=currency
                    ).filter(
                        date__range=(begin_quarter(quarter), quarter)
                    ).aggregate(Avg('rate'))
            quarterly_exchange_rates[(currency, quarter)] = quarter_rate['rate__avg']
    return quarterly_exchange_rates

class Command(BaseCommand):
    """
    Load IMF exchange rates into the database
    """
    def handle(self, *args, **options):
        """
        """
        if not args or len(args) != 1:
            raise CommandError("Please provide a filename to parse")

        filepath = args[0]

        if not os.path.isfile(filepath):
            raise CommandError("No file found at: {filename}".format(filename=filepath))

        exchange_rates = parse_tsv(filepath)
        if not exchange_rates:
            raise CommandError("Unable to parse exchange rates from file")

        currencies = set()
        dates = set()
        for currency, date in exchange_rates.keys():
            currencies.add(currency)
            dates.add(date)


        print("The following date range was found in the file:")
        d_format = "%B %d, %Y"
        print(min(dates).strftime(d_format), " to ", max(dates).strftime(d_format))
        print()
        print("The following currencies were found in the file:")
        for currency in currencies:
            print(currency)


        bulk_update(ExchangeRate, exchange_rates, ("currency", "date"), "rate", prompt=True)

        # update quarterly Exchange Rates

        quarterly_exchange_rates = calc_quarterly_exchange_rates(exchange_rates)

        change_quarters = set()
        for i, date in quarterly_exchange_rates.keys():
            change_quarters.add(date)

        print("The following Quarterly Exchange Rates need to be updated:")
        print("(This will only affect the currencies listed above)")
        for quarter in change_quarters:
            print(str(quarters.get_q(quarter)) + "Q", quarter.year)

        bulk_update(QuarterlyExchangeRate, quarterly_exchange_rates, ("currency", "date"), "rate", prompt=True)
