from app.models import Data
from django import template
register = template.Library()

def get_data(id):
    name=Data.get_data(id).name
    if len(name)>15:
        name=name[:15]+'...'
    return name
def get_keys(data):
    keys=data.keys()
    return keys
def get_rows(data):
    keys=list(data.keys())
    n=len(data[keys[0]])
    rows=[]
    try:
        for i in range(n):
            row=[]
            for key in keys:
                row.append(data[key][str(i)])
            rows.append(row)
    except:
        pass
    return rows
register.filter('get_data', get_data)
register.filter('get_keys', get_keys)
register.filter('get_rows', get_rows)