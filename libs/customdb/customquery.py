from operator import itemgetter
import re
import datetime

def sqltodict(query,param,sort=False,index='id',dateformat="%m-%d-%Y %H:%M"):
    pattern = re.compile('datetime') 
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(query,param)
    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        cleaned_row = []
        for index, data in enumerate(row):
            if pattern.search(str(type(data))):
                data = data.strftime(dateformat)
            cleaned_row.append(data)
        for field in zip(fieldnames, cleaned_row):
            rowset.append(field)
        result.append(dict(rowset))
    if sort:
         result = sorted(result, key=itemgetter(index))
    return result

def sqltojson(query,param,sort=False,sortindex='id',dateformat="%m-%d-%Y %H:%M"):
    pattern = re.compile('datetime') 
    from django.utils import simplejson
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(query,param)
    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        cleaned_row = []
        for index, data in enumerate(row):
            if pattern.search(str(type(data))):
                data = data.strftime(dateformat)
            cleaned_row.append(data)
        for field in zip(fieldnames, cleaned_row):
            rowset.append(field)
        result.append(dict(rowset))
    if sort:
        result = sorted(result, key=itemgetter(sortindex))
    return simplejson.dumps(result)

def executesql(query,param):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(query,param)

def sqltolist(query,param):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(query,param)
    print cursor.description
    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        cleaned_row = []
        for index, data in enumerate(row):
            cleaned_row.append(data)
        for field in zip(fieldnames, cleaned_row):
            rowset.append(field)
        result.append(rowset)
    return result
