from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^code/$', views.send_code),
    url(r'^users/$', views.login),
]
