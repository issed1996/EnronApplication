from django.conf.urls import url
from django.urls import path
from . import views



app_name='application1'

urlpatterns = [
    url(r'^home$', views.home, name='home'),
    url(r'^employees$', views.employees, name='employees'),
    url(r'couples', views.couples, name='couples'),
    url(r'days', views.days, name='days'),
    url(r'profiles', views.profiles, name='profiles'),

]