# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context,loader,RequestContext

#引入我们创建的表单类
from .forms import *

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
        if request.GET.get('env') == "online":
            env_en = 'online'
            env_cn= '正式'
            env_en_next = 'test'
            print('online')
        else:
            env_en = 'test'
            env_cn = '测试'
            env_en_next = 'online'
            print('test')

        t = loader.get_template("release.html")
        c = RequestContext(request,{'env_en':env_en,'env_cn':env_cn,'env_en_next':env_en_next,'form':form})
        return HttpResponse(t.render(c))
        #return render(request,'release.html',locals())
