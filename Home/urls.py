from django.urls import  path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('home/', views.home),
    path('IP_DNS/',views.IP_DNS),
    path('Process_Link/',views.Process_Link),
]