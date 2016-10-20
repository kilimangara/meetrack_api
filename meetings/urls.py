from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.meetings_list),
    url(r'^(?P<pk>\d+)/$', views.single_meeting),
    url(r'^(?P<pk>\d+)/users/$', views.meeting_members),
]
