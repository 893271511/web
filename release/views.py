# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import Context,loader,RequestContext
from release.models import *
#引入我们创建的表单类
from .forms import *
import json

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
            return HttpResponse(env + " " +project + " " + str(version))
            #return HttpResponse(form.cleaned_data)
    else:
        form = ReleaseForm()
        t = loader.get_template("release.html")
        c = RequestContext(request,{'form':form})
        return HttpResponse(t.render(c))
        #return render(request,'release.html',locals())

def OneRelease(request):
    # 当提交表单时
    if request.method == 'POST':
        # form 包含提交的数据
        form = OneReleaseForm(request.POST)
        # 如果提交的数据合法
        if form.is_valid():
            project = form.cleaned_data['project']
            env = form.cleaned_data['env']
            version = form.cleaned_data['version']
            return HttpResponse(env + " " +project + " " + str(version))
            #return HttpResponse(form.cleaned_data)
    else:
        form2 = OneReleaseForm()
        t = loader.get_template("onerelease.html")
        c = RequestContext(request,{'form':form2})
        return HttpResponse(t.render(c))
        #return render(request,'release.html',locals())

def Switch(request):
    # 当提交表单时
    if request.POST.get("env") == "test":
        env_en = 'online'
        env_cn = '正式'
    else:
        env_en = 'test'
        env_cn = '测试'
    return JsonResponse({'env_en':env_en,'env_cn':env_cn})

def SelectProject(request):
    project = request.POST.get("project")
    if request.POST.get("env") == "test":
        SERVER_CHOICES = Project.objects.get(name=project).test_env.all().values_list('ip')
    else:
        SERVER_CHOICES = Project.objects.get(name=project).online_env.all().values_list('ip')
    print(SERVER_CHOICES)
    print(json.dumps(SERVER_CHOICES))
    return JsonResponse(SERVER_CHOICES)
