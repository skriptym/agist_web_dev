from django.urls import path,include
from . import views
from .views import BaseView,RegistrationView,LoginView,Base_maps,Personal,lk
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',BaseView.as_view(),name='base'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(next_page='/'),name='logout'),
    path('registration/',RegistrationView.as_view(),name='registration'),
    path('agro_map/',Base_maps.maps_base,name='agro_map'),
    path('lk/',lk.lk_panel,name='lk'),
    path('My_crop/',lk.table,name='table'),
    path('My personal/',lk.personal,name='personal'),
    path('Add personal/',lk.add_personal,name='addpersonal'),
    path('Add Crop/',Personal.add_crop,name='addcrop'),
    path("<str:pk>/",views.movir_statistic_crop.as_view(),name='statistic_crop'),


]
