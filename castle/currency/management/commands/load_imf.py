# -*- coding: utf-8 -*-
from __future__ import print_function
import csv
import datetime
from difflib import SequenceMatcher
import re
from os.path import isfile

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from currency.models import Currency, ExchangeRate, QuarterlyExchangeRate


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
            return

        currency_row = imf.next()
        for col, currency_string in enumerate(currency_row):
            parsed_currency = parse_currency(currency_string)
            if parsed_currency:
                currency_lookup[col] = parsed_currency

        if not currency_lookup:
            return

        for row, line in enumerate(imf):
            exchange_rate_date = parse_date(line[pivot[1]])
            if not exchange_rate_date:
                continue

            offset = pivot[1] + 1 
            for col, exchange_rate in enumerate(line[offset:]):
                true_col = col + offset
                if not true_col in currency_lookup:
                    continue
                parsed_exchange_rate = parse_exchange_rate(exchange_rate)
                if parsed_exchange_rate:
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

class Command(BaseCommand):
    """
    Load IMF exchange rates into the database
    """
    def handle(self, *args, **options):
        """
        """
#        if not args or len(args) != 1:
#            raise CommandError("Please provide a filename to parse")
#        
#        filename = args[0]
#        
#        if not isfile(filename):
#            raise CommandError("No file found at: {filename}".format(filename=filename))
