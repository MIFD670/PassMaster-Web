from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list, name='list'),
    url(r'^add/', views.add, name='add'),
    url(r'^(?P<group_id>[0-9]+)/update/', views.update, name='update'),
    url(r'^(?P<group_id>[0-9]+)/join/$', views.join, name='joinGroup'),
    url(r'^(?P<group_id>[0-9]+)/approve/(?P<user_id>[0-9]+)/$', views.approve, name='approve'),
    url(r'^(?P<group_id>[0-9]+)/leave/$', views.leave, name='leaveGroup'),
    url(r'^(?P<group_id>[0-9]+)/leave/(?P<new_owner_id>[0-9]+)/$', views.pickNewOwner, name='pickNewOwner'),
    url(r'^(?P<group_id>[0-9]+)/$', views.group, name='groupView'),
    url(r'^(?P<group_id>[0-9]+)/console/$', views.console, name='consoleView'),
    url(r'^(?P<group_id>[0-9]+)/chat/$', views.chat, name='groupChat'),
    url(r'^(?P<group_id>[0-9]+)/switchPermissionLevel/(?P<user_id>[0-9]+)/$', views.changePermissionLevel, name='switchPermissionLevel'),

]
