"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url,include
from django.views.generic import TemplateView
import xadmin
from django.views.static import serve
from users.views import IndexView
from MxOnline.settings import MEDIA_ROOT,STATIC_ROOT
from organization.views import OrgView
from users.views import LoginView,RegisterView,ActiveUserView,ForgetPwdView,ResetView,ModifyPwdView,LogoutView


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^$',IndexView.as_view(),name='index'),
    url(r'^login/$',LoginView.as_view(),name='login'),
    url(r'^logout/$',LogoutView.as_view(),name='logout'),
    url(r'^register/$',RegisterView.as_view(),name='register'),
    url(r'^captcha/',include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),
    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),
    url(r'^reset/(?P<active_code>.*)/$',ResetView.as_view(),name='reset_pwd'),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),
    #课程机构首页
    url(r'^org/',include('organization.urls',namespace='org')),
    #课程相关url配置
    url(r'^course/',include('courses.urls',namespace='course')),

    #配置上传文件的处理函数
    url(r'^media/(?P<path>.*)$', serve,{'document_root':MEDIA_ROOT}),

    url(r'^static/(?P<path>.*)$', serve,{'document_root':STATIC_ROOT}),

    url(r'^users/',include('users.urls',namespace='users')),
    #富文本相关
    # url(r'^ueditor/',include('DjangoUeditor.urls')),

]
#全局404页面配置
handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'

if settings.DEBUG:
    # debug_toolbar 插件配置
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
else:
    # 项目部署上线时使用
    from MxOnline.settings import STATIC_ROOT
    # 配置静态文件访问处理
    urlpatterns.append(url(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}))