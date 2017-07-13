import json

from django.urls import reverse

from .forms import UserInfoForm
from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from users.models import UserProfile,EmailVerifyRecord
from users.forms import LoginForm,RegisterForm,ForgetForm,ModifyPwdForm,UploadImageForm
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from django.http import HttpResponse,HttpResponseRedirect
from operation.models import UserCourse,UserFavorite,UserMessage
from organization.models import CourseOrg,Teacher
from courses.models import Course
from pure_pagination import PageNotAnInteger,Paginator,EmptyPage
from .models import Banner


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LogoutView(View):
    def get(self,request):
        logout(request)
        from django.core.urlresolvers import reverse
        return HttpResponseRedirect(reverse('index'))


class LoginView(View):
    def get(self,request):
        return render(request,'login.html',{})
    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            user_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=user_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    #重定向
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request,'login.html',{'msg':'当前账号未激活'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误!'})
        else:
            return render(request,'login.html',{'login_form':login_form})


class ActiveUserView(View):
    def get(self,request,active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request,'active_fail.html')
        return render(request,'login.html',{})


class RegisterView(View):
    def get(self,request):
        register_form = RegisterForm()
        return render(request,'register.html',{'register_form':register_form})
    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email','')
            if UserProfile.objects.filter(email=user_name):
                return render(request,'register.html',{'register_form':register_form,'msg':'当前用户已经存在'})
            user_word = request.POST.get('password','')
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active=False
            user_profile.password = make_password(user_word)
            user_profile.save()

            #写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = '欢迎注册慕学在线网用户 在这里开启您的IT梦想'
            user_message.save()

            send_register_email(user_name,'register')
            return render(request,'login.html')
        else:
            return render(request,'register.html',{'register_form':register_form})


class ForgetPwdView(View):
    def get(self,request):
        forget_form = ForgetForm()
        return render(request,'forgetpwd.html',{'forget_form':forget_form})

    def post(self,request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email','')
            send_register_email(email,'forget')
            return render(request,'send_success.html')
        else:
            return render(request,'forgetpwd.html',{'forget_form':forget_form})


class ResetView(View):
    def get(self,request,active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request,'password_reset.html',{'email':email})
        else:
            return render(request,'active_fail.html')
        return render(request,'login.html')


class ModifyPwdView(View):
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1','')
            pwd2 = request.POST.get('password2','')
            email = request.POST.get('email','')
            if pwd1 != pwd2:
                return render(request,'password_reset.html',{'email':email,'msg':'两次输入的密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            return render(request,'login.html')
        else:
            email = request.POST.get('email','')
            return render(request,'password_reset.html',{'email':email,'modify_form':modify_form})


class UserInfoView(View):
    """
    用户个人信息
    """
    def get(self,request):
        current_page = 'userinfo'
        return render(request,'usercenter-info.html',{
            'current_page':current_page
        })

    def post(self,request):
        user_info_form = UserInfoForm(request.POST,instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors),content_type='application/json')


class UploadImageView(LoginRequiredMixin,View):
    """
    用户修改头像
    """
    def post(self,request):
        image_form = UploadImageForm(request.POST,request.FILES,instance=request.user)
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            image_form.save()
            # request.user.image = image
            # request.user.save()
            return HttpResponse('{"status":"success","msg":"修改成功"}',content_type='application/json')
        else:
            return HttpResponse('{"status":"success"}',content_type='application/json')


class UpdatePwdView(LoginRequiredMixin,View):
    """
    个人中心修改用户密码
    """
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)
        pwd1 = request.POST.get('password1','')
        pwd2 = request.POST.get('password2','')
        if modify_form.is_valid():
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}',content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return HttpResponse('{"status":"success"}',content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin,View):
    """
    发送邮箱验证码
    """
    def get(self,request):
        email = request.GET.get('email','')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}',content_type='application/json')
        send_register_email(email,'update_email')
        return HttpResponse('{"status":"success"}',content_type='application/json')


class UpdateEmailView(LoginRequiredMixin,View):
    """
    修改个人邮箱
    """
    def post(self,request):
        email = request.POST.get('email','')
        code = request.POST.get('code','')
        existed_records = EmailVerifyRecord.objects.filter(email=email,code=code,send_type='update_email')
        if  existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码出错了"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin,View):
    """
    我的课程
    """
    def get(self,request):
        current_page = 'mycourse'
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request,'usercenter-mycourse.html',{
            'user_courses':user_courses,
            'current_page':current_page,
        })


class MyFavOrgView(LoginRequiredMixin, View):
        """
        我收藏的课程机构
        """

        def get(self, request):
            org_list = []
            current_page = ''
            user_fav_orgs = UserFavorite.objects.filter(user=request.user,fav_type=2)
            for user_fav_org in user_fav_orgs:
                org_id = user_fav_org.fav_id
                org = CourseOrg.objects.get(id=org_id)
                org_list.append(org)
            return render(request, 'usercenter-fav-org.html', {
                'org_list': org_list,
                'current_page':current_page
            })


class MyFavTeacherView(LoginRequiredMixin,View):

    def get(self,request):
        teacher_list =[]
        current_page = ''
        user_fav_teachers = UserFavorite.objects.filter(user=request.user,fav_type=3)
        for user_fav_teacher in user_fav_teachers:
            teacher_id = user_fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request,'usercenter-fav-teacher.html',{
            'teacher_list':teacher_list,
            'current_page':current_page
        })


class MyFavCourseView(View):

    def get(self,request):
        course_list = []
        current_page = ''
        user_fav_courses = UserFavorite.objects.filter(user=request.user,fav_type=1)
        for user_fav_course in user_fav_courses:
            course_id = user_fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request,'usercenter-fav-course.html',{
            'course_list':course_list,
            'current_page':current_page
        })


class MyMessageView(LoginRequiredMixin,View):
    """
    我的消息
    """
    def get(self,request):
        current_page = 'mymessage'
        all_message = UserMessage.objects.filter(user=request.user.id)
        #用户进入个人消息后清空未读消息的记录
        all_unread_message = UserMessage.objects.filter(user=request.user.id,has_read=False)
        for unread_message in all_unread_message:
            unread_message.has_read = True
            unread_message.save()
        #对个人消息进行分页
        try:
            page = request.POST.get('page',1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_message,5,request=request)
        messages = p.page(page)
        return render(request,'usercenter-message.html',{
            'messages':messages,
            'current_page':current_page
        })


class IndexView(View):
    def get(self,request):
        #取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:9]
        banner_coures = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request,'index.html',{
            'all_banners':all_banners,
            'courses':courses,
            'banner_courses':banner_coures,
            'course_orgs':course_orgs
        })


def page_not_found(request):
    #全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html',{})
    response.status_code = 404
    return response

def page_error(request):
    #全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html',{})
    response.status_code = 500
    return response


# class LoginUnsafeView(View):
#     def get(self,request):
#         return render(request,'login.html',{
#         })
#     def post(self,request):
#         user_name = request.POST.get('username','')
#         pass_word = request.POST.get('password','')
#         import pymysql
#         coon = pymysql.connect(
#             host='127.0.0.1',
#             user='root',
#             passwd='2414605975',
#             db='mxonline',
#             charset='utf8'
#         )
#         cursor = coon.cursor()
#         sql_select = "select * from users_userprofile where email='{0}' and password='{1}'".format(user_name,pass_word)
#         result =cursor.execute(sql_select)
#         for row in cursor.fetchall():
#             #查询到用户
#             pass

# Create your views here.
# def user_login(request):
#     if request.method == 'POST':
#         user_name = request.POST.get('username','')
#         user_word = request.POST.get('password','')
#         user = authenticate(username=user_name,password=user_word)
#         if user is not None:
#             login(request,user)
#             return render(request,'index.html',{'username':user_name})
#         else:
#             return render(request, 'login.html', {'msg':'用户名或密码错误'})
#     elif request.method == 'GET':
#         return render(request,'login.html',{})
