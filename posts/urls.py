from django.conf.urls import url
from django.contrib import admin
app_name = 'posts'

from .views import (
	post_list,
	post_create,
	post_detail,
	post_update,
	post_delete,
	exam_schedule,
	)

urlpatterns = [
	url(r'^$', post_list, name='list'),
    url(r'^create/$', post_create,name='create'),
    url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/edit/$', post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', post_delete,name = 'delete'),
	url(r'^exam_schedule',exam_schedule),#for showing exam_schedule

    #url(r'^posts/$', "<appname>.views.<function_name>"),
]
