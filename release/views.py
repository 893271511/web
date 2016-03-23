# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context,loader

#引入我们创建的表单类
from .forms import *

def Index(request):
    # 当提交表单时
    if request.method == 'POST':
        # form 包含提交的数据
        form = ReleaseForm(request.POST)
        # 如果提交的数据合法
        if form.is_valid():
            project = form.cleaned_data['project']
            version = form.cleaned_data['version']
            return HttpResponse(project + " " + str(version))
    else:
        form = ReleaseForm()

    return render(request, 'index.html', {'form': form})