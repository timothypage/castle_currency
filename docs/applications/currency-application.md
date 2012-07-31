#Currency Application

The currency application is a repository of currencies and associated exchange rates used within the Castle application.

##Models

Basic features of currency application database models.

###Currency Model

Currencies are represented by a Django model object. It includes the name, abbreviation and a number of formatting options (including the excel formatting string).

Required Fields:
* Name
* Abbreviation (unique)
* Active state (defaults to False)

Optional Fields:
* Symbol
* Various formatting options

Future:
* A unique slug
* A better organization of formatting options
* A way to integrate a fixed rate (e.g. HKD is roughly 7.75), however this may be time-dependent

###Exchange Rate Model

Exchange Rates are obtained daily from the IMF.
They have a [daily rate endpoint in tsv](http://www.imf.org/external/np/fin/data/rms_rep.aspx?tsvflag=Y) and a [historical search](http://www.imf.org/external/np/fin/ert/GUI/Pages/CountryDataBase.aspx).

We use the IMF's representative rates (currency per US Dollar), however, some currencies are given by the IMF as the inverse (US Dollar per currency unit) and must be converted before being saved.

Required Fields:
* Currency FK
* Date
* Rate (must be > 0.0)

_The combination of currency and date is unique_

###Quarterly Exchange Rate Model

Most of the data stored by the application is on a quarterly basis:
* Q1: Jan. 1st to March 31st
* Q2: April 1st to June 30th
* Q3: July 1st to Sept. 30th
* Q4: Oct. 1st to Dec. 31st

Therefore, a 'quarterly' exchange rate is needed for these data points, which we obtain by averaging the daily values over their respective time spans.

* Currency FK
* Date (_technically, quarter_)
* Rate (must be > 0.0)

_The combination of currency and date is unique_


##Operations

Besides a simply repository of information, the currency application must provide the functions to upload the rates from historical IMF data and parse the given daily rates.

These operations should share as much code as possible.

Changing/adding currencies can be off-loaded to the Django admin console.

###Management Jobs

Loading exchanges rates from the downloaded IMF historical data should not require any manipulation of the downloaded data. A single management job is satisfactory.

###Tasks

A asynchronous process is needed for the scraping the daily IMF tsv of exchange rates. This should be run daily on an auxiliary (or non-concurrent) celery queue.


##Current State

The formatting options are a mess, but until a "holistic" (holy fuck, shoot me in the face) solution can be found for downstream formatting, knowing what to store in the currency model is simply a guess.

In short, a monetary data in US Dollars might look like $1,234.56 (in millions), while a Euro data point would need to alter not only the symbol, but the position of the symbol (before or after the amount), as well as the characters used for the decimal (e.g. ".") and group delimitation (e.g. ","). Worse, some currencies have large exchange rates that could change the magnitude (needing representation in billions instead of millions), or even the number of digits in each group (the INR prefers a million to be formatted as 10,00,000).

But these problems are mainly in the table generation code, the currency application is mainly a store of data.

The usage of floating points for storing exchange rates has given rise to issues when comparing the stored values against those loaded from the IMF data. Using decimal fields (were the decimal point is fixed) would fix this comparison issue, but introduces a potentially unknown cast from decimals to floating points (as monetary data metrics are also stored in floating point).

The goal is to make the application as autonomous as possible.

###Interactions with other applications

The Currency application should interface with the various custom model fields for representing quarters (currently not included in this repo).

It should also make use of a generic update function. This function will need an understanding of how to compare floating points.

###Future Endeavors

Besides accurately recording the given exchange rates, the only other features for the application would be:
* Improved historical introspection (error checking functions)
* Visualization options (sparklines)
* Non-admin console interaction (CRUD for currencies)