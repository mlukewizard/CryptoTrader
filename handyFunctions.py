#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#This is where you can put handy functions which might be useful for anyone
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import datetime

def dateTimeRange(startdate, enddate):
    if isinstance(startdate, str):
        startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
    if isinstance(enddate, str):
        enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
    if isinstance(startdate, datetime.datetime):
        startdate = startdate.date()
    if isinstance(enddate, datetime.datetime):
        enddate = enddate.date()
    day = startdate
    dateList = []
    while day != enddate:
        dateList.append(day)
        day = day + datetime.timedelta(days=1)
    return dateList