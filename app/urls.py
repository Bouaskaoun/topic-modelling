from app import views
from django.urls import path, re_path
urlpatterns = [
    path('',views.home,name='home'),
    path('ajax/page/<str:page>',views.load_page,name='page'),
    path('ajax/get_columns',views.get_columns_names,name='get_columns'),
    path('ajax/save_data',views.save_data,name='save_data'),
    path('ajax/delete_data/<int:id>',views.delete_data,name='delete_data'),
    path('ajax/select_data/<int:id>',views.select_data,name='select_data'),
    path('ajax/generate_report',views.generate_report_,name='generate_report'),
    path('ajax/clean_data/',views.clean_data,name='clean_data'),
    path('test',views.test,name='test')
]
