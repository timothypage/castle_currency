# -*- coding: utf-8 -*
import datetime
# Since this file is imported into a models file, keep it free of
# local imports, to prevent circular references

Q1 = (3, 31)
Q2 = (6, 30)
Q3 = (9, 30)
Q4 = (12, 31)

VALID_QUARTERS = set([Q1, Q2, Q3, Q4])

Q_LOOKUP = {1: Q1, 2: Q2, 3: Q3, 4: Q4}
MD_LOOKUP = {Q1: 1, Q2: 2, Q3: 3, Q4: 4}


def convert_to_yq(qdate):
    """
    Convert a quarter date into a tuple of year, quarter
    """
    md = (qdate.month, qdate.day)
    if md not in MD_LOOKUP:
        # TODO errors?
        return None
        
    return qdate.year, MD_LOOKUP[md]


def build_q_label(quarter):
    """
    """
    q = MD_LOOKUP[(quarter.month, quarter.day)]
    label = "{0}Q {1}".format(q, quarter.year)
    return {'label': label, 'year': quarter.year, 'quarter': q}


def build_q_string(quarter, full_year=True):
    """
    """
    q = MD_LOOKUP[(quarter.month, quarter.day)]
    return "{0}Q {1}".format(q, quarter.year) if full_year else "{0}Q{1}".format(q, str(quarter.year)[2:])


def quarters_between(start, end):
    """
    Returns the integer number of quarters between two dates
    """
    if end < start:
        # TODO errors?
        return None
    
    if end == start:
        return 0
    
    start_year, start_q = convert_to_yq(start)
    end_year, end_q = convert_to_yq(end)
    
    years = (end_year - start_year)
    quarters = end_q - (start_q - 1)
    return years * 4 + quarters


def get_qdates(year):
    """
    Return a list of all quarters as a datetime.date in the given year.
    """
    return [datetime.date(year, m, d) for m, d in sorted(MD_LOOKUP.keys())]


def get_q(qdate):
    """
    Return the integer quarter that the given datetime.date represents.
    """
    return MD_LOOKUP.get((qdate.month, qdate.day), None)
