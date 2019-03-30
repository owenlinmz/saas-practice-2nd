# -*- coding: utf-8 -*-
import datetime
import json
import time
import base64

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from blueking.component.shortcuts import get_client_by_request
from common.mymako import render_mako_context
from common.mymako import render_json
from common_esb import *
from django.forms.models import model_to_dict

from home_application.models import HostInfo


def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


def history(request):
    return render_mako_context(request, '/home_application/history.html')


def test(request):
    return render_json({"result": 'ok', "username": request.user.username})


@csrf_exempt
def get_biz(request):
    client = get_client_by_request(request)
    res = search_business_esb(client, request.user.username)
    return render_json(res)


@csrf_exempt
def get_set(request):
    bk_biz_id = request.GET.get('bk_biz_id')
    client = get_client_by_request(request)
    res = search_set_esb(client, request.user.username, bk_biz_id)
    return render_json(res)


@csrf_exempt
def get_host(request):
    params = json.loads(request.body)
    bk_host_innerip__in = params.get('bk_host_innerip__in')
    client = get_client_by_request(request)
    res = search_host_esb(client, request.user.username)
    result = []
    for item in res['data']:
        params = {
            'bk_host_innerip': item['host']['bk_host_innerip'],
            'bk_host_name': item['host']['bk_host_name'],
            'bk_os_name': item['host']['bk_os_name'],
            'bk_inst_name': item['host']['bk_cloud_id'][0]['bk_inst_name'],
            'bk_cloud_id': item['host']['bk_cloud_id'][0]['id'],
            'bk_biz_id': item['biz'][0]['bk_biz_id'],
            'bk_biz_name': item['biz'][0]['bk_biz_name'],
            'last_user': request.user.username
        }
        host_info, is_exist = HostInfo.objects.update_or_create(**params)
        if is_exist:
            host_info.last_user = request.user.username
            host_info.save()

    if bk_host_innerip__in:
        bk_host_innerip__in = bk_host_innerip__in.split(',')
        host_info = HostInfo.objects.filter(bk_host_innerip__in=bk_host_innerip__in, is_delete=False)
    else:
        host_info = HostInfo.objects.filter(is_delete=False)
    for host in host_info:
        result.append(model_to_dict(host))

    return render_json({'data': result})


@csrf_exempt
def list_host(request):
    bk_biz_id = request.GET.get('bk_biz_id')
    client = get_client_by_request(request)
    res = search_host_esb(client, request.user.username, bk_biz_id)
    result = []
    for item in res['data']:
        params = {
            'bk_host_innerip': item['host']['bk_host_innerip']
        }
        result.append(params)
    return render_json({'data': result})


@csrf_exempt
def add_host(request):
    params = json.loads(request.body)
    ip = params['ip']
    host_info = HostInfo.objects.filter(bk_host_innerip=ip, is_delete=False)
    if host_info:
        result = u'主机已存在'
    else:
        HostInfo.objects.filter(bk_host_innerip=ip).update(is_delete=False)
        result = u'添加成功'
    return render_json({'data': result})


@csrf_exempt
def delete_host(request):
    params = json.loads(request.body)
    ip = params['ip']
    HostInfo.objects.filter(bk_host_innerip=ip).update(is_delete=True)
    return render_json({'data': u'删除成功'})


class CommonUtil(object):

    @classmethod
    def pop_useless_params(self, params):
        # 请求参数处理
        pop_keys = []
        for key, value in params.items():
            if value == '':
                pop_keys.append(key)
            if key.endswith('__in'):
                params[key] = str(value).split(',')
        for pop in pop_keys:
            params.pop(pop)
        return params
