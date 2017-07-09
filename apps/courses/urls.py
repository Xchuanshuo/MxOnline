#_*_ coding:utf-8 _*_
from django.conf.urls import url
from courses.views import CourseListView

__author__ = 'Legend'
__date__ = '2017/7/9 9:49'


urlpatterns = [
    url(r'list/$',CourseListView.as_view(),name='course_list')
]