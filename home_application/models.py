# -*- coding: utf-8 -*-
from django.db import models


class HostInfo(models.Model):
    bk_host_innerip = models.CharField(u'IP地址', max_length=50, primary_key=True, null=False)
    bk_host_name = models.CharField(u'主机名', max_length=50)
    bk_os_name = models.CharField(u'系统名', max_length=50)
    bk_inst_name = models.CharField(u'云区域名称', max_length=50)
    bk_biz_id = models.IntegerField(u'业务ID')
    bk_biz_name = models.CharField(u'业务名称', max_length=50)
    bk_cloud_id = models.IntegerField(u'云区域ID')
    last_user = models.CharField(u'用户名', max_length=50, default='admin')
    is_delete = models.BooleanField(u'是否删除', default=False)


class HostLoad5(models.Model):
    bk_host_innerip = models.ForeignKey(HostInfo, max_length=20, on_delete=models.CASCADE)
    load5 = models.CharField(u'5分钟负载', max_length=10)
    check_time = models.DateTimeField(u'检测时间', auto_now=True)


class HostDisk(models.Model):
    bk_host_innerip = models.ForeignKey(HostInfo, max_length=20, on_delete=models.CASCADE)
    disk = models.TextField(u'硬盘情况')
    check_time = models.DateTimeField(u'检测时间', auto_now=True)


class HostMem(models.Model):
    bk_host_innerip = models.ForeignKey(HostInfo, max_length=20, on_delete=models.CASCADE)
    mem = models.TextField(u'内存情况')
    check_time = models.DateTimeField(u'检测时间', auto_now=True)
