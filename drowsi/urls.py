"""drowsi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))


    <button  class="sep" 
              style=
              " padding: 10px; 

              color: white;
              padding: 25px 32px;
              text-align: center;
              text-decoration: none;
              display: inline-block;

              font-size: 26px; " 
              onclick= "location.href='{% url 'script' %}'">START</button>
"""
from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [

    path('admin/', admin.site.urls),
    path('',views.button),
    path('main/',views.input, name="main"),
    path('contact/test1.html/',views.last, name="last"),
    path('contact/',views.contact, name="contact"),
    path('output/',views.output, name="script")
]


