#_*_ coding:utf-8 _*_
__author__ = 'Legend'
__date__ = '2017/7/5 12:02'

from .models import Course, Lesson, Video, CourseResource, BannerCourse
import xadmin


class LessonInline(object):
    model = Lesson
    extra = 0

class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree','learn_times','students','fav_nums','image','click_nums','add_time','teacher']
    search_fields = ['name', 'desc', 'detail', 'degree','learn_times','students']
    list_filter = ['name', 'desc', 'detail', 'degree','learn_times','students','fav_nums','click_nums','add_time']
    #进去课程页面时排序
    ordering = ['-click_nums']
    #设置字段操作权限
    readonly_fields = ['click_nums','fav_nums']
    list_editable = ['degree']
    #同一个model注册2个管理器(只能嵌套一层）
    inlines = [LessonInline]
    #设置字段在课程信息中隐藏
    # exclude = ['click_nums']
    style_fields = {'detail':'ueditor'}

    def queryset(self):
        qs = super(CourseAdmin,self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        #在保存课程时统计课程机构的课程数
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                    'add_time', 'teacher']
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'click_nums', 'add_time']
    # 进去课程页面时排序
    ordering = ['-click_nums']
    # 设置字段操作权限
    readonly_fields = ['click_nums', 'fav_nums']
    # 同一个model注册2个管理器(只能嵌套一层）
    inlines = [LessonInline]

    def queryset(self):
        qs = super(BannerCourseAdmin,self).queryset()
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    list_display = ['course','name','add_time']
    search_fields = ['course','name']
    list_filter = ['course','name','add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name','download','add_time']
    search_fields = ['course', 'name','download']
    list_filter = ['course', 'name','download','add_time']

xadmin.site.register(Course,CourseAdmin)
xadmin.site.register(BannerCourse,BannerCourseAdmin)
xadmin.site.register(Lesson,LessonAdmin)
xadmin.site.register(Video,VideoAdmin)
xadmin.site.register(CourseResource,CourseResourceAdmin)