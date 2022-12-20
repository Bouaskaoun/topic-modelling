import pandas as pd
import json
def load_file(request):
    data=None
    if request.method.lower()=='post':
        filename,data = get_file_info(request.body.decode())
        if filename.endswith('.csv'):
            datarows=[row.split(',') for row in data.split('\n')]
            data= json.loads(pd.DataFrame(datarows[1:],columns=datarows[0]).to_json())
        elif filename.endswith('.json'):
            data=json.loads(pd.json_normalize(json.loads(data)).to_json())
    return data
def get_file_info(body:str):
    info=body.split('\r\n\r\n')[0].replace('"','').replace(' ','').split('\r\n')
    filename=info[1].split(';')[2].split('=')[1]
    data=body.split('\r\n\r\n')[1].split('\r\n')[0]
    return filename, data
def get_columns(request):
    data=load_file(request)
    return data.keys() if data!=None else None
