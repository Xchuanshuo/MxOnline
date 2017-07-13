#_*_ coding:utf-8 _*_
__author__ = 'Legend'
__date__ = '2017/7/5 12:26'

from .models import CityDict,CourseOrg,Teacher
import xadmin


class CityDictAdmin(object):
    list_display = ['name','desc','add_time']
    search_fields = ['name','desc']
    list_filter = ['name','desc','add_time']


class CourseOrgAdmin(object):
    list_display = ['name','desc','click_nums','fav_nums','image','address','city','add_time']
    search_fields = ['name','desc','address','city']
    list_filter = ['name','desc','click_nums','fav_nums','image','address','city','add_time']
    #设置外键可搜索
    # relfield_style = 'fk-ajx'


class TeacherAdmin(object):
    list_display = ['org','name','work_years','work_comany','work_position','points','click_nums','fav_nums','add_time']
    search_fields = ['org','name','work_years','work_comany','work_position']
    list_filter = ['org','name','work_years','work_comany','work_position','add_time']

xadmin.site.register(CityDict,CityDictAdmin)
xadmin.site.register(CourseOrg,CourseOrgAdmin)
xadmin.site.register(Teacher,TeacherAdmin)