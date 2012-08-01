# -*- coding: utf-8 -*-
from __future__ import print_function
from os.path import isfile

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from currency.models import Currency, ExchangeRate, QuarterlyExchangeRate


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


class Command(BaseCommand):
    """
    Load IMF exchange rates into the database
    """
    def handle(self, *args, **options):
        """
        """
        if not args or len(args) != 1:
            raise CommandError("Please provide a filename to parse")
        
        filename = args[0]
        
        if not isfile(filename):
            raise CommandError("No file found at: {filename}".format(filename=filename))
        
        pass