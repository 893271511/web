# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect, request
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login,logout
from django.contrib import auth
from release.models import *
# 引入我们创建的表单类
from .forms import *
import os,sys,time
from django.http import StreamingHttpResponse

def stream_response_generator(release_info):
    #rows = (os.popen("/tmp/aa.sh %s %s %s" %(release_info[0],release_info[1],release_info[2])))
    script_path = "/root/PycharmProjects/web/release/release_scripts"
    rows = (os.popen("%s/coderelease.sh %s %s %s" %(script_path,release_info[0],release_info[1],release_info[2])))
    for row in rows:
        #yield "<div>%s</div>\n" % row
        yield "%s" % row


@login_required(login_url='/')
def Release(request):
    # 当提交表单时
    if request.method == 'POST':
        # form 包含提交的数据
        form = ReleaseForm(request.POST)
        # 如果提交的数据合法
        if form.is_valid():
            project = form.cleaned_data['project']
            env = form.cleaned_data['env']
            version = form.cleaned_data['version']
            return StreamingHttpResponse(stream_response_generator([project,version,env]),)
    else:
        url = request.get_full_path()
        request.breadcrumbs([(("项目发布"),'/release/'),
                             (("单服务器发布"),'/onerelease/'),
                             (('发布版本查询'),'#'),
                             (('项目端口查询'),'##'),
                             ])
        if request.GET.get('env') == 'online':
            env_en = 'online'
            env_cn = '正式'
            env_next = 'test'
        else:
            env_en = 'test'
            env_cn = '测试'
            env_next = 'online'
        form = ReleaseForm()
        t = loader.get_template("release.html")
        #c = RequestContext(request, {'form': form})
        c = RequestContext(request, locals())
        return HttpResponse(t.render(c))

@login_required
def OneRelease(request):
    # 当提交表单时
    if request.method == 'POST':
        project = request.POST.get('project')
        env = request.POST.get('env')
        version = request.POST.get('version')
        server = request.POST.get('server')
        if env == "test":
            SERVER = Project.objects.get(name=project).test_env.all()
        else:
            SERVER = Project.objects.get(name=project).online_env.all()
        for i in SERVER:
            if server == str(i):
               print(env + " " + project + " " + str(version) + " " + str(server))
               return HttpResponse(env + " " + project + " " + str(version) + " " + str(server))
        return HttpResponse("禁止发到此主机")
    else:

        form2 = OneReleaseForm()
        url = request.get_full_path()
        request.breadcrumbs([(("项目发布"),'/release/'),
                             (("单服务器发布"),'/onerelease/'),
                             (('发布版本查询'),'#'),
                             (('项目端口查询'),'##'),
                             ])
        t = loader.get_template("onerelease.html")
        c = RequestContext(request, {'form': form2,'url':url})
        return HttpResponse(t.render(c))

@login_required
def Switch(request):
    # 当提交表单时
    if request.POST.get("env") == "test":
        env_en = 'online'
        env_cn = '正式'
    else:
        env_en = 'test'
        env_cn = '测试'
    return JsonResponse({'env_en': env_en, 'env_cn': env_cn})

@login_required
def SelectProject(request):
    SERVER_CHOICES = {}
    project = request.POST.get("project")
    if request.POST.get("env") == "test":
        SERVER = Project.objects.get(name=project).test_env.all()
    else:
        SERVER = Project.objects.get(name=project).online_env.all()
    for i in SERVER:
        i = str(i)
        SERVER_CHOICES[i] = i
    return JsonResponse(SERVER_CHOICES)


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")



