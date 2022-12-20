from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from app.file_manger import get_columns
from app.models import Data
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from app.topic_modeling import  generate_report, get_initial_report
import json

def home(request):
    return render(request,'pages/index.html')
def load_page(request,page):
    data=get_data(request,page)
    html= render_to_string('components/content/'+page+'.html', {'data':data}, request)
    return HttpResponse(html,content_type='application/html')
def save_data(request):
    if request.method.lower()=='post':
        name=request.POST.get('name')
        column=request.POST.get('column')
        file=request.FILES.get('fileupload')
    status=Data.save_data(name,column,file)
    response=redirect('home')
    response['Location']=response['Location']+'?page=documents&operation=add&status='+str(status)
    return response
def delete_data(request,id):
    response=redirect('home')
    try:
        if 'selected_data' in request.session and int(request.session['selected_data'])==id:
            del request.session['selected_data']
        data=Data.get_data(id)
        data.delete()
        response['Location']=response['Location']+'?page=documents&operation=delete&status=True'
        return response
    except:
        response['Location']=response['Location']+'?page=documents&operation=delete&status=False'
    return response
def select_data(request,id):
    response=redirect('home')
    try:
        data=Data.get_data(id)
        request.session['selected_data']=data.id
        response['Location']=response['Location']+'?page=documents&operation=select&status=True'
        return response
    except:
        response['Location']=response['Location']+'?page=documents&operation=select&status=False'
    return response
@csrf_exempt
def get_columns_names(request):
    data=get_columns(request)
    html= render_to_string('components/parts/column-select.html', {'columns':data}, request)
    return HttpResponse(html,content_type='application/html')
def get_data(request,page):
    data=None
    if page=='documents':
        data=Data.get_all()
    if page=='visualisation':
        if 'selected_data' in request.session:
            data={
                'raw':Data.load_raw_data(int(request.session['selected_data']),limit=100),
                'clean':Data.load_clean_data(int(request.session['selected_data']),limit=100),
            }
    if page=='preprocessing':
        if 'selected_data' in request.session:
            data={
                'data':Data.get_data(int(request.session['selected_data'])),
                'clean_data':Data.load_clean_data(int(request.session['selected_data']),limit=100),
            }
    if page=='report':
        if 'selected_data' in request.session:
            item=Data.get_data(int(request.session['selected_data']))
            item.get_raw_data()
            raw_top_words=get_initial_report(20,item)
            clean_top_words=None
            if item.cleaned:
                item.get_clean_data()
                clean_top_words=get_initial_report(20,item,raw=False)
            data={
                'data':item,
                'clean_data':{
                    'top_words':clean_top_words['plot'],
                    'words':clean_top_words['words'],
                    'words_values':clean_top_words['values'],
                } if  clean_top_words else None,
                'raw_data':{
                    'top_words':raw_top_words['plot'],
                    'words':raw_top_words['words'],
                    'words_values':raw_top_words['values'],
                },
            }
    return data
def clean_data(request):
    try:
        data=Data.get_data(int(request.session['selected_data']))
        data.clean_data()
        response=redirect('home')
        response['Location']=response['Location']+'?page=preprocessing&operation=clean&status=True'
        return response 
    except Exception as e:
        print(e)
    response=redirect('home')
    response['Location']=response['Location']+'?page=preprocessing&operation=clean&status=False'
    return response
def generate_report_(request):
    ajax_data = json.load(request)
    print(ajax_data)
    data=None
    html=None
    samples_length=int(ajax_data['samples_length'])
    result=None
    topics_number=int(ajax_data['topics_number'])
    method=ajax_data['method']
    try:
        data=Data.get_data(int(request.session['selected_data']))
        result=generate_report(data,topics_number,method.lower(),samples_length)
        html= render_to_string('components/parts/report-content.html', {"topics":topics_number,'method':method,'samples_length':samples_length,'data':result}, request)
    except Exception as e:
        html= render_to_string('components/parts/report-content.html', {"topics":0,'method':method,'samples_length':0,'data':None}, request)
        print(e)
        pass
    data={'html':html}
    return JsonResponse(data)
def test(request):
    data=Data.get_data(int(request.session['selected_data']))
    a=generate_report(data,3,'lda',1000)
    plot=a['tsne']
    return HttpResponse(f'<img src="data:image/png;base64,{plot}"/>')


