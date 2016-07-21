# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect, request
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login,logout
from django.contrib import auth
from django.contrib.auth import *
from release.models import *
from .forms import *
import os,sys,time
from django.http import StreamingHttpResponse
import logging
from django.db.models import *
#from django.contrib.auth.decorators import permission_required
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User

from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm, get_perms
from guardian.core import ObjectPermissionChecker
from guardian.decorators import permission_required
from guardian.decorators import permission_required_or_403


logger = logging.getLogger('django')


@login_required
def user_role():
    return request.user.is_superuser

def stream_response_generator(release_info):
    try:
        script_path = "/root/PycharmProjects/web/release/release_scripts"
        #判断是单台发布，还是批量发布
        if len(release_info) == 3:
            shell_cmd = "%s/coderelease.py %s %s %s %s" %(script_path,release_info[0],release_info[1],release_info[2],"all")
        else:
            shell_cmd = "%s/coderelease.py %s %s %s %s" %(script_path,release_info[0],release_info[1],release_info[2],release_info[3])

        rows = (os.popen(shell_cmd))
        for row in rows:
            #yield "<div>%s</div>\n" % rows
            yield "%s" % row
    except Exception as e:
        logger.error(e)

# @login_required(login_url='/')
# def Rollback(request):
#     # 当提交表单时
#     if request.method == 'POST':
#         # form 包含提交的数据
#         form = ReleaseForm(request.POST)
#         print("aaa")
#         server = request.POST.get('server')
#         print(server)
#         print("bbb")
#         # 如果提交的数据合法
#         if form.is_valid():
#             project = form.cleaned_data['project']
#             env = form.cleaned_data['env']
#             version = form.cleaned_data['version']
#             return StreamingHttpResponse(stream_response_generator([project,version,env]),)
#     else:
#         url = request.get_full_path()
#         request.breadcrumbs([(("项目发布"),'/release/'),
#                              (("单服务器发布"),'/onerelease/'),
#                              (('回滚代码'),'/rollback'),
#                              (('下载代码'),'#####'),
#                              (('增量发布'),'######'),
#                              (('发布历史查询'),'#'),
#                              (('项目端口查询'),'##'),
#                              (('项目日志查看'),'#######'),
#                              ])
#         # if request.GET.get('env') == 'online':
#         #     env_en = 'online'
#         #     env_cn = '正式'
#         #     env_next = 'test'
#         # else:
#         #     env_en = 'test'
#         #     env_cn = '测试'
#         #     env_next = 'online'
#         # form = ReleaseForm()
#         t = loader.get_template("release.html")
#         # #c = RequestContext(request, {'form': form})
#         c = RequestContext(request, locals())
#         return HttpResponse(t.render(c))

breadcrumbs = [
                 (("项目发布"),'/index/'),
                 (("单服务器发布"),'/onerelease/'),
                 (('回滚代码'),'/rollback/'),
                 (('下载代码'),'#####'),
                 (('增量发布'),'######'),
                 (('发布历史查询'),'#'),
                 (('项目端口查询'),'##'),
                 (('项目日志查看'),'#######'),
              ]

def set_title(url):
    for i in range(len(breadcrumbs)-1):
        if breadcrumbs[i][1] == url:
            title = breadcrumbs[i][0]
            break
        else:
            title = "title错误"
    return title

@login_required
#@permission_required('release.release_test_project',)
#@permission_required('release.release_staging_project',login_url='/index/')
#@permission_required('release.release_staging_project',return_403=True)
#@permission_required_or_403()
@permission_required('release.release_test_project',(Project, 'name', 'renren-licai'),return_403=True)
#@permission_required('release.release_test_project',(Project, 'id', '1'),return_403=True)
#@permission_required_or_403('release.release_test_project',(Project, 'name', 'renren-licai'), accept_global_perms=False)
def Release(request):
    # 当提交表单时
    project = request.POST.get('project')
    env = request.POST.get('env')
    version = request.POST.get('version')
    server = request.POST.get('server')
    #判断是单台发布，还是批量发布
    if server != None:
        if env == "test":
            SERVER = Project.objects.get(name=project).test_env.all()
        elif env == "staging":
            SERVER = Project.objects.get(name=project).staging_env.all()
        else:
            SERVER = Project.objects.get(name=project).production_env.all()
        for i in SERVER:
            if server == str(i):
                return StreamingHttpResponse(stream_response_generator([project,version,env,server]),)
        return HttpResponse("禁止发到此主机")
    else:
        return StreamingHttpResponse(stream_response_generator([project,version,env]),)




@login_required
def index(request):
    url = request.get_full_path()
    request.breadcrumbs(breadcrumbs)
    if request.GET.get('env') == 'production':
        env_en = 'production'
        env_cn = '生产'
        env_next = 'test'
    else:
        env_en = 'test'
        env_cn = '测试'
        env_next = 'production'

    if url == "/onerelease/":
        title = set_title(url)
        form = OneReleaseForm()
        t = loader.get_template("onerelease.html")
    else:
        title = set_title(url)
        form = ReleaseForm()

        pro = Project.objects.get(name='renren-licai')
        joe = User.objects.get(username=request.user)
        checker = ObjectPermissionChecker(joe) # we can pass user or group
        var2 = checker.has_perm('release.release_test_project', pro)
        var3 = request.user.has_perm('release.release_test_project')
        #assign_perm('release.release_test_project', user, pro_name)

        t = loader.get_template("release.html")
    c = RequestContext(request, locals())
    return HttpResponse(t.render(c))

@login_required
def Rollback(request):
    #当提交表单时
    if request.method == 'POST':
        project = request.POST.get('project')
        env = request.POST.get('env')
        version = request.POST.get('version')
        server = request.POST.get('server')
        #判断是单台发布，还是批量发布
        if server != None:
            if env == "test":
                SERVER = Project.objects.get(name=project).test_env.all()
            elif env == "staging":
                SERVER = Project.objects.get(name=project).staging_env.all()
            else:
                SERVER = Project.objects.get(name=project).production_env.all()
            for i in SERVER:
                if server == str(i):
                    return StreamingHttpResponse(stream_response_generator([project,version,env,server]),)
            return HttpResponse("禁止发到此主机")
        else:
            return StreamingHttpResponse(stream_response_generator([project,version,env]),)

    else:
        url = request.get_full_path()
        request.breadcrumbs(breadcrumbs)
        if request.GET.get('env') == 'production':
            env_en = 'production'
            env_cn = '生产'
            env_next = 'test'
        else:
            env_en = 'test'
            env_cn = '测试'
            env_next = 'production'
        title = set_title(url)
        form = GeneralForm()
        t = loader.get_template("rollback.html")
        c = RequestContext(request, locals())
        return HttpResponse(t.render(c))

#@user_role()
@login_required()
def Switch(request):
    # 当提交表单时
    if request.POST.get("env") == "test":
        env_en = 'staging'
        env_cn = '预发布'
    elif request.POST.get("env") == "staging":
        env_en = 'production'
        env_cn = '生产'
    elif request.POST.get("env") == "production":
        env_en = 'test'
        env_cn = '测试'
    return JsonResponse({'env_en': env_en, 'env_cn': env_cn})


@login_required
def SelectProject(request):
    SERVER_CHOICES = {}
    project = request.POST.get("project")
    if request.POST.get("env") == "test":
        SERVER = Project.objects.get(name=project).test_env.all()
    elif request.POST.get("env") == "staging":
        SERVER = Project.objects.get(name=project).staging_env.all()
    else:
        SERVER = Project.objects.get(name=project).production_env.all()
    for i in SERVER:
        i = str(i)
        SERVER_CHOICES[i] = i
    return JsonResponse(SERVER_CHOICES)


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")




