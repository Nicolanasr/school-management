from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'class'

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:class_name>/', views.class_info, name='class_info'),
    path('add/new', views.add_new_mat, name="add_new_mat"),
    path('getdetails', views.getdetails, name="getdetails"),
    path('add/new_chapter', views.new_chapter, name="new_chapter"),
    path('add/new_module', views.new_module, name="new_module"),
    # path('add/new_for_class/', views.new_for_class, name='new_for_class'),
    # path('add/<str:classe>/new_for_chapter/', views.new_for_chapter, name='new_for_chapter'),
    # path('add/<str:chapter>/new_for_module/', views.new_for_module, name='new_for_module'),
    # path('adding_materials/<str:class_name>/<str:chapter_name>/<str:module_name>/', views.adding_materials, name='adding_materials'),
]

