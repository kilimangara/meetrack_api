from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^account/$', views.account),
    url(r'^users/$', views.users_list),
    url(r'^users/(?P<pk>\d+)/$', views.user_details),
]
