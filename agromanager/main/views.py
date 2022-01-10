from django.shortcuts import render
from django.http import  HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django import views
from django.views.generic.base import View
from .forms import  LoginForm, RegistrationForm
import pandas as pd
import json
import numpy as np
from area import area
import requests
from datetime import datetime
import psycopg2
import time

host="178.154.215.138"
user="agist_web"
password="Vtntj@Fuhjyjvbz!100814"
db_name="agist_general"
connection = psycopg2.connect(user=user,password=password,host=host,port="5432",database=db_name)


class BaseView(views.View):

    def get(self,request,*args,**kwargs):
        #context = {'form': form, 'cart': self.cart}
        return render(request, 'base.html', {})



class LoginView(views.View):


    def get(self,request,*args,**kwargs):
        form=LoginForm(request.POST or None)
        context = {
            'form':form,
        }
        return render(request,'login.html',context)
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user=authenticate(username=username,password=password)
            if user:
                login(request,user)
                return HttpResponseRedirect('/')
            context = {
                'form': form,
            }
            return render(request,'login.html',context)

class RegistrationView(views.View):

    def get(self,request,*args,**kwargs):
        form = RegistrationForm(request.POST or None)

        context = {
            'form':form,
        }
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user=form.save(commit=False)
            new_user.username=form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request,user)
            return HttpResponseRedirect('/')
        context = {
            'form': form,
        }
        return render(request, 'registration.html', context)



def read_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_crop")
        rows=cursor.fetchall()
        df=pd.DataFrame(rows)

        return df


def read_db_crop(user_get, key):
    with connection.cursor() as cursor:
        if key==1:
            curent="SELECT * FROM user_crop_data WHERE user_name = '"+str(user_get)+ "' AND flag='1'"
        else:
            curent="SELECT * FROM user_crop_data"

        cursor.execute(curent)
        rows=cursor.fetchall()
        df=pd.DataFrame(rows,columns=['user_name','id_crop','crop','flag',
                                      'x_min','y_min','x_max','y_max',
                                      'datetime_create','area','name_crop','culture'])
        return df




def coord(data):
    for feature in data['features']:
      for cood in feature['geometry']['coordinates']:
        return cood


def central_point(usermame):
    df=read_db_crop(usermame,1)

    size=df.shape
    df=df.reset_index(drop=True)
    array_crop=[]
    for i in range(0,size[0]):
        data=json.loads((df.crop)[i])
        vert=coord(data)
        point=(np.sum(vert,axis=0))/np.array(vert).shape[0]
        array_crop.append(point)
    #print('>>>>>>',np.array(array_crop))
    #print(";;;;;;;",(np.max(np.array(array_crop)[:,0])))
    central=(np.sum(array_crop,axis=0))/size[0]
    #print(central)
    long = central[0]
    lat = central[1]
    return long,lat


def box_crop(json_crop):
    data = json.loads(json_crop)
    vert = coord(data)
    long_max=np.array(vert)[:,0].max()
    long_min=np.array(vert)[:,0].min()
    lati_max=np.array(vert)[:,1].max()
    lati_min=np.array(vert)[:,1].min()
    return long_min,lati_min,long_max,lati_max


class lk(views.View):

    def lk_panel(request):
        return render(request, 'lk.html')


    def table(request):
        user = request.user

        if str(user) != 'AnonymousUser':
            crop=read_db_crop(user,1)

            if crop.shape[0]!=0:
                new_df=pd.DataFrame()
                new_df["namecrop"]=crop.name_crop.values[:]
                new_df["area"]=crop.area.values[:]
                new_df["culture"]=crop.culture.values[:]
                new_df["idcrop"]=crop.id_crop.values[:]
                crop_to_json=new_df.to_json(orient = "records", force_ascii=False)
                crop_in_ist=json.loads(crop_to_json)
            else:
                crop_in_ist=[]
            if request.is_ajax():
                if request.method == 'GET':

                    data_to_str = json.dumps(request.GET)
                    data_to_json = json.loads(data_to_str)
                    id_crop = data_to_json["id_crop"]
                    with connection.cursor() as cursor:
                        update_query = "UPDATE user_crop_data SET flag = '0' WHERE id_crop = '"+str(id_crop)+"'"
                        cursor.execute(update_query)
                        connection.commit()


            context = {'crop': crop_in_ist}
            return render(request, 'table.html',context)


    def personal(request):
        return render(request, 'personal.html')

    def add_personal(request):
        return render(request, 'addpersonal.html')

class movir_statistic_crop(View):
    def get(self,request,pk):

        user = request.user

        if str(user) == 'AnonymousUser':
            crop2={'prise':'пощел нахрен хрен моржовый'}
        else:
            crop=read_db_crop(user,1)

            new_df=pd.DataFrame()
            new_df["name_crop"]=crop.name_crop.values[:]
            new_df["area"]=crop.area.values[:]
            new_df["culture"]=crop.culture.values[:]

            crop = crop[crop['name_crop'] == pk]





        context = {'pp': crop}
        return render(request, 'statistic_crop.html',context)



class Personal(views.View):

    def add_crop(request):
        user = request.user
        if request.is_ajax():
            if request.method == 'GET':
                data_to_str= json.dumps(request.GET)
                data_to_json=json.loads(data_to_str)
                name_crop=data_to_json["name_crop"]
                culture_crop=data_to_json["culture_crop"]
                coord=data_to_json["data1"]
                js_data = json.loads(coord)
                geoJSON=js_data["features"][0]['geometry']
                area_crop=round((area(geoJSON) / 10000),2)
                current_user = request.user
                index_crop=read_db_crop(current_user,0).shape[0]

                if index_crop == 0:
                    id_crop=1
                else:
                    id_crop=index_crop+1
                bbox=box_crop(coord)

                with connection.cursor() as cursor:
                    ins="("+"'"+str(current_user)+"'"+","+"'"+str(id_crop)+"'"+","+"'"+str(coord)+"'"+","+"'"\
                        +str(1)+"'"+","+"'"+str(bbox[0])+"'"+","+"'"+str(bbox[1])+"'"+","+"'"+str(bbox[2])+"'"\
                        +","+"'"+str(bbox[3])+"'"+","+"'"+ str(datetime.now())+"'"+","+"'"+str(area_crop)+"'"\
                        +","+"'"+ str(name_crop)+"'"+","+"'"+str(culture_crop)+"'"+")"



                    insert_query="INSERT INTO user_crop_data (user_name,id_crop,crop,flag,x_min," \
                                 "y_min,x_max,y_max,datetime_create,area,name_crop,culture) VALUES "+ins

                    cursor.execute(insert_query)
                    connection.commit()


        time.sleep(1)
        geojson_data= read_db_crop(user,1)

        dat3=[]
        xmin=[]
        xmax=[]
        ymin=[]
        ymax=[]
        for i in range(0,geojson_data.shape[0]):
            dat=geojson_data.copy()
            dat2 = dat.crop.values[i]
            xmin.append(float(dat.x_min.values[i]))
            xmax.append(float(dat.x_max.values[i]))
            ymin.append(float(dat.y_min.values[i]))
            ymax.append(float(dat.y_max.values[i]))
            dat3.append(dat2)
        dm=str(dat3).replace("'{","{").replace("}'","}")
        if geojson_data.shape[0]==0:
            ppozx = 84.7832195
            ppozy = 56.530288
        else:
            ppozx=(np.mean(xmin)+np.mean(xmax))/2
            ppozy = (np.mean(ymin) + np.mean(ymax)) / 2

        context = {'geojson': dm,
                   'pozx':ppozx,
                   'pozy':ppozy}

        return render(request,'addcrop.html',context)

class Base_maps(views.View):

    def maps_base(request):
        user = request.user
        geojson_data = read_db_crop(user,1)

        dat3 = []
        xmin = []
        xmax = []
        ymin = []
        ymax = []
        for i in range(0, geojson_data.shape[0]):
            dat = geojson_data.copy()
            dat2 = dat.crop.values[i]
            color=',"style": {"color": "red"}'

            dat2=dat2[:-3]+color+"}]}"
            xmin.append(float(dat.x_min.values[i]))
            xmax.append(float(dat.x_max.values[i]))
            ymin.append(float(dat.y_min.values[i]))
            ymax.append(float(dat.y_max.values[i]))
            dat3.append(dat2)
        dm = str(dat3).replace("'{", "{").replace("}'", "}")
        if geojson_data.shape[0]==0:
            ppozx = 84.7832195
            ppozy = 56.530288
        else:
            ppozx=(np.mean(xmin)+np.mean(xmax))/2
            ppozy = (np.mean(ymin) + np.mean(ymax)) / 2

        context = {'geojson': dm,
                   'pozx':ppozx,
                   'pozy':ppozy}

        return render(request,'maps.html',context)


def my_crops(request):
    pass